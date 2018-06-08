"""
Example queries to pass to query_to_data:
"""

from datetime import datetime

from django.utils import timezone
from django.http import QueryDict
from django.shortcuts import get_object_or_404

from sis_pull.models import (
    Student, User, Site, GradeLevel, Section,
    AttendanceFlag, AttendanceDailyRecord, SectionLevelRosterPerYear,
    OverallScoreCache, GradebookSectionCourseAffinity, Course,
    CategoryScoreCache)
from reports.models import Report
from utils import get_academic_year, GRADE_TO_GPA_POINTS

GROUPS_AND_MODELS = {
    'site': Site,
    'grade_level': GradeLevel,
    'section': Section,
    'student': Student,
}


def query_to_data(query):
    """
    Takes in a QueryDict (ie, request.GET) and returns happy data!
    :param query: QueryDict<request.GET>
    :return: Data dict
    """
    report_query = {}
    report_id = query.get('report_id')
    if report_id:
        report = get_object_or_404(Report, pk=report_id)
        report_query = query_parser(QueryDict(report.query))
    else:
        # turn query into proper dict:
        report_query = query_parser(query)
        # check category, pass to proper function
    if not report_query:
        raise ValueError("Query or report id required")

    if report_query["type"] == "attendance":
        report_data = attendance_query_to_data(report_id, **report_query)

    if report_query["type"] == "grades":
        report_data = grades_query_to_data(**report_query)

    report_data['query'] = report.query if report_id else query.urlencode()

    return report_data


def get_student_ids_for_group_and_id(group, object_id, site_id=None,
                                     return_set=True):

    """
    Takes an object of type Student, Section, grade_level, or Site, and returns
    the students associated with that object
    :return: List[int<student_ids>]
    """
    if group_is_model(group, "student"):
        return [object_id]

    if group_is_model(group, "grade_level"):
        return GradeLevel.objects.get(pk=object_id)\
            .get_current_student_ids(site_id=site_id)

    model = get_object_from_group_and_id(group, object_id)

    if return_set:
        return set(model.get_current_student_ids())

    return model.get_current_student_ids()


def attendance_query_to_data(report_id=None, **query_params):
    """
    Takes a dict of query_params and returns fresh data.
    :param query_params:
    :return: Attendance data dict
    """

    DATE_FORMAT = "%Y-%m-%d"
    DISPLAY_DATE_FORMAT = "%b %-d, %Y"  # YYYY-MM-DD

    def get_time_string():
        """For formatting in titles"""
        if from_date and not to_date:
            return f"{from_date.strftime(DISPLAY_DATE_FORMAT)} to now"
        if is_single_day:
            return f" On {from_date.strftime(DISPLAY_DATE_FORMAT)}"

        if from_date.year == to_date.year:
            from_string = from_date.strftime(DISPLAY_DATE_FORMAT).split(',')[0]
            return f"{from_string} " +\
                   f"to {to_date.strftime(DISPLAY_DATE_FORMAT)}"

        return f"{from_date.strftime(DISPLAY_DATE_FORMAT)} to " + \
               f"{to_date.strftime(DISPLAY_DATE_FORMAT)}"

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
        to_date = datetime.strptime(to_date, DATE_FORMAT).date()

    student_ids = get_student_ids_for_group_and_id(group, group_id,
                                                site_id=site_id)

    time_string = get_time_string()
    group_name = get_object_from_group_and_id(group, group_id)
    data = {
        "title": f"Attendance: {group_name}",
        "subheading": time_string,
        "group": group,
        "group_id": group_id,
        "from_date": from_date,
        "to_date": to_date,
        "columns": AttendanceFlag.get_flag_columns(),  # can we cache somehow?
        "exclude_columns": AttendanceFlag.get_exclude_columns(),
    }

    if is_single_day:
        data["data"] = AttendanceDailyRecord.get_student_records_for_date(
            student_ids, from_date
        )
    else:
        data["data"] = AttendanceDailyRecord.get_summaries_for_students(
            student_ids, from_date, to_date
        )

    if report_id:
        data["id"] = report_id

    return data


def grades_query_to_data(report_id=None, **query_params):
    """Currently supports getting most up to date data for grade"""

    group = query_params["group"]
    group_id = query_params["group_id"]
    site_id = query_params.get("site_id", None)
    course_id = query_params.get("course_id", None)

    student_ids = get_student_ids_for_group_and_id(group, group_id,
                                                   return_set=True)

    def _get_all_recent_course_grades_for_student_id(student_id):
        # Get all active sections for student
        now = timezone.now()
        active_section_ids = (SectionLevelRosterPerYear.objects
                           .filter(student_id=student_id)
                           .filter(entry_date__lte=now, leave_date__gte=now)
                           .distinct('section_id')
                           .values_list('section_id', flat=True))

        # Get all associated gradebooks
        gradebook_ids = (GradebookSectionCourseAffinity.objects
                         .filter(section_id__in=active_section_ids)
                         .order_by('course_id', '-id')
                         .distinct('course_id')
                         .values_list('gradebook_id', flat=True))

        # Get most recent score per gradebook
        return (OverallScoreCache.objects
                .filter(student_id=student_id)
                .filter(gradebook_id__in=gradebook_ids)
                .exclude(possible_points__isnull=True)
                .order_by('gradebook_id', '-calculated_at')
                .distinct('gradebook_id')
                .all())

    def _get_most_recent_category_grades(student_id,
                                         course_id=None,
                                         gradebook_id=None):

        if not course_id and not gradebook_id:
            raise ValueError("Must have either course_id or gradebook_id.")

        if gradebook_id:
            gradebook_ids = [gradebook_id]
        else:
            gradebook_ids = (GradebookSectionCourseAffinity.objects
                            .filter(course_id=course_id)
                            .distinct('gradebook_id')
                            .values_list('gradebook_id', flat=True))

        return (CategoryScoreCache.objects
                .filter(student_id=student_id)
                .filter(gradebook_id__in=gradebook_ids)
                .exclude(possible_points__isnull=True)
                .order_by('category_id', '-calculated_at')
                .distinct('category_id')
                .all()
                )

    def _calculate_gpa_from_grade_list(osc_list):
        if len(osc_list) == 0:
            return "NA"
        gpas = [GRADE_TO_GPA_POINTS[osc.mark] for osc in osc_list]
        return round(sum(gpas) / len(gpas), 3)

    def _shape_group_gpas(osc_list):
        """Takes list of gradebook scores from same student, returns GPA"""
        if len(osc_list) == 0:
            return None

        _id = osc_list[0].student_id
        label = osc_list[0].student.last_first
        gpa = _calculate_gpa_from_grade_list(osc_list)
        calculated_at = osc_list[0].calculated_at

        shape = {
            "id": _id,
            "label": label,
            "measures": [{"measure_label": "GPA", "measure": gpa}],
            "calculated_at": calculated_at,
            "children": [_shape_student_grades(o) for o in osc_list]
        }

        return shape

    def _shape_student_grades(overall_score_cache, children=False):
        osc = overall_score_cache

        shape = {
            "id": osc.student_id,
            "label": str(osc.gradebook),
            "measures": [
                {"measure_label": "Mark", "measure": osc.mark},
                {"measure_label": "Percentage", "measure": osc.percentage},
            ],
            "calculated_at": osc.calculated_at,
        }

        if children:
            gb_id = osc.gradebook_id

            category_grades = _get_most_recent_category_grades(
                group_id, gradebook_id=gb_id
            )

            shape["children"] = [_shape_category_grades(c)
                                 for c in category_grades]
        return shape

    def _shape_category_grades(category_score_cache):
        csc = category_score_cache

        shape = {
            "id": csc.category_id,
            "label": csc.category_name,
            "measures": [
                {"measure_label": "Mark", "measure": csc.mark},
                {"measure_label": "Percentage", "measure": csc.percentage},
                {"measure_label": "Missing Assignments",
                 "measure": csc.missing_count},
                {"measure_label": "Weight", "measure": csc.weight}
            ],
            "calculated_at": csc.calculated_at
        }
        return shape

    def _get_group_name():
        if group == "section":
            return str(Section.objects.get(pk=group_id))
        if group == "grade_level":
            return str(GradeLevel.objects.get(pk=group_id))
        if group == "school":
            return str(Site.objects.get(pk=group_id))
        return str(Student.objects.get(pk=group_id))

    group_name = _get_group_name()

    # Grouping of student grades - all course grades
    # Constituent part: GPAs
    if group != "student":
        data = [_get_all_recent_course_grades_for_student_id(sid)
                for sid in student_ids]
        # filter out empty data sets
        formatted_data = [_shape_group_gpas(i) for i in data if len(i) > 0]
        title_string = f"Academic grades for {group_name} (latest)"

    # Individual student grades - all course grades
    # Constituent parts: Course marks and percentages
    elif not course_id:
        data = _get_all_recent_course_grades_for_student_id(group_id)
        formatted_data = [_shape_student_grades(i, children=True) for i in data]
        title_string = f"Academic grades for {group_name} (latest)"

    # Individual student grades - single course
    # Constituent parts: Category grades
    else:
        data = _get_most_recent_category_grades(group_id, course_id)
        formatted_data = [_shape_category_grades(d) for d in data]
        course_name = Course.objects.get(pk=course_id).short_name
        title_string = f"{course_name} grades for {group_name} (latest)"

    response = {
        "title": title_string,
        "group": group,
        "group_id": group_id,
        "data": formatted_data
    }

    if report_id:
        response["report_id"] = report_id

    return response


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
    model_for_group = GROUPS_AND_MODELS.get(group)
    if model_for_group:
        return model_for_group.objects.get(pk=object_id)

    raise ValueError(f"Group {group} is not supported.")

