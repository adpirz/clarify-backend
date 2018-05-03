"""
Example queries to pass to query_to_data:
"""

from datetime import datetime

from django.utils import timezone

from sis_pull.models import (
    Student, User, Site, GradeLevel, Section,
    AttendanceFlag, AttendanceDailyRecord, SectionLevelRosterPerYear
)
GROUPS_AND_MODELS = (
    ("site", Site),
    ("grade_level", GradeLevel),
    ("section", Section),
)


def query_to_data(query):
    """
    Takes in a QueryDict (ie, request.GET) and returns happy data!
    :param query: QueryDict<request.GET>
    :return: Data dict
    """
    # turn query into proper dict:
    query_dict = query_parser(query)
    # check category, pass to proper function

    if query_dict["category"] == "attendance":
        return attendance_query_to_data(**query_dict)

    raise ValueError("Only supports attendance.")


def get_students_for_group_and_id(group, object_id, site_id=None):
    """
    Gets a list of current student instances based on group and
    object_id for that group.
    :param group: str; group name ('section', 'site', etc.)
    :param object_id: id of group
    :param site_id: optional, used for 'grade_level'
    :return: Iterable<students>
    """
    if group_is_model(group, "student"):
        return [Student.objects.get(pk=object_id)]

    if group_is_model(group, "grade_level"):
        return GradeLevel.objects.get(pk=object_id)\
            .get_current_students(site_id=site_id)

    model = get_object_from_group_and_id(group, object_id)
    return model.objects.get(pk=object_id)\
        .get_current_students()


def get_student_ids_for_group_and_id(group, object_id, site_id=None):
    """
    Like 'get_students_for_group_and_id', but returns a list of ids.
    :return: List[int<student_ids>]
    """
    if group_is_model(group, "student"):
        return [object_id]

    if group_is_model(group, "grade_level"):
        return GradeLevel.objects.get(pk=object_id)\
            .get_current_student_ids(site_id=site_id)

    model = get_object_from_group_and_id(group, object_id)
    return model.objects.get(pk=object_id) \
        .get_current_student_ids()


def attendance_query_to_data(**query_params):
    """
    Takes a dict of query_params and returns fresh data.
    :param query_params:
    :return: Attendance data dict
    """

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # YYYY-MM-DD

    def get_time_string():
        """For formatting in titles"""
        if from_date and not to_date:
            return f"from {from_date.strftime(DATE_FORMAT)} to now"
        if is_single_day:
            return f" on {from_date.strftime(DATE_FORMAT)}"

        return f"from {from_date.strftime(DATE_FORMAT)} to " + \
               f"{to_date.strftime(DATE_FORMAT)}"

    group = query_params["group"]
    group_id = query_params["group_id"]
    from_date = query_params.get("from_date", None)
    to_date = query_params.get("to_date", None)
    site_id = query_params.get("site_id", None)
    is_single_day = from_date == to_date
    from_date = datetime.strptime(from_date, DATE_FORMAT).date()

    if not to_date:
            to_date = timezone.now().date()
    else:
        to_date = datetime.strptime(from_date, DATE_FORMAT).date()

    student_ids = get_student_ids_for_group_and_id(group, group_id,
                                                site_id=site_id)

    time_string = get_time_string()

    data = {
        "Title": f"Attendance for {group} {group_id} {time_string}",
        "group": group,
        "group_id": group_id,
        "from_date": from_date,
        "to_date": to_date,
        "flags": AttendanceFlag.get_flags_dict()  # can we cache somehow?
    }

    if is_single_day:
        data["data"] = AttendanceDailyRecord.get_student_records_for_date(
            student_ids, from_date
        )
    else:
        data["data"] = AttendanceDailyRecord.get_summaries_for_students(
            student_ids, from_date, to_date
        )

    return data


def query_parser(querydict):
    """Returns a Python dict from a QueryDict"""
    query_dict = dict(querydict)
    return {k: query_value_parser(v) for k, v in query_dict.items()}


def query_value_parser(value):
    """Parse raw values into Python primitives"""
    if isinstance(value, list) and len(value) > 1:
        return [query_value_parser(i) for i in value]
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.isdigit():
        return int(value)
    if isinstance(value, str) and len(value.split(',')) > 1:
        return query_value_parser(value.split(','))

    return value


def group_is_model(group_name, model_name):
    """
    Checks if group_name is model_name or plural of model_name
    :param group_name: str - group name
    :param model_name: str - model name
    :return: Boolean
    """
    return group_name in [model_name, model_name + "s"]


def get_object_from_group_and_id(group, object_id):
    """
    Get instance from model name and id.
    :param group: str - group name
    :param object_id: int - id
    :return: Django Model
    """
    for group_title, model in GROUPS_AND_MODELS:
        if group == group_title:

            return model.objects.get(pk=object_id)

    raise ValueError(f"Group {group} is not supported.")

