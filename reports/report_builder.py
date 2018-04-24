from django.http import QueryDict

from sis_pull.models import (
    Student, User, Site, GradeLevel, Section,
    AttendanceFlag, AttendanceDailyRecord, SectionLevelRosterPerYear
)
GROUPS_AND_MODELS = (
    ("site", Site),
    ("school", Site),
    ("grade_level", GradeLevel),
    ("section", Section),
)


def query_to_data(query, user):
    # turn query into proper dict:

    # get group
    pass


def get_students_for_group_and_id(group, object_id, site_id=None):
    if group_is_model(group, "student"):
        return Student.objects.get(pk=object_id)

    if group_is_model(group, "section"):
        return Section.objects.get(pk=object_id)\
            .get_current_students(site_id=site_id)

    return group.objects.get(pk=object_id)\
        .get_current_students()

def attendance_query_to_data(**query_params):
    group = query_params["group"]
    group_id = query_params[]


def query_parser(query_string):
    """

    :param query_string:
    :return:
    """

    query_dict = dict(QueryDict(query_string))
    return {k: query_value_parser(v) for k, v in query_dict.items()}


def query_value_parser(value):
    if isinstance(value, list) and len(value) > 1:
        return [query_value_parser(i) for i in value]
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    if value in ["t", "true", "True"]:
        return True
    if value in ["f", "false", "False"]:
        return False
    if value.isdigit():
        return int(value)
    if isinstance(value, str) and len(value.split(',')) > 1:
        return query_value_parser(value.split(','))

    return value


def group_is_model(group_name, model_name):
    return group_name in [model_name, model_name + "s"]

def get_object_from_group_and_id(group, object_id):


    for group_model in GROUPS_AND_MODELS:
        group_title, model = group_model
        if group_is_model(group, group_title):
            return model.objects.get(pk=object_id)

    raise ValueError(f"Group {group} is not supported.")

