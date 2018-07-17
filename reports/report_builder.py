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
    CategoryScoreCache, ScoreCache, Category, Gradebook)
from reports.models import Report
from utils import get_academic_year, GRADE_TO_GPA_POINTS

GROUPS_AND_MODELS = {
    'site': Site,
    'grade_level': GradeLevel,
    'section': Section,
    'student': Student,
}


def query_to_data(request):
    """
    Takes in a QueryDict (ie, request.GET) and returns happy data!
    :param query: QueryDict<request.GET>
    :return: Data dict
    """
    query = request.GET
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

    report_query["staff"] = request.user.staff

    if report_query["type"] == "attendance":
        report_data = attendance_query_to_data(report_id, **report_query)

    elif report_query["type"] == "grades":
        report_data = grades_query_to_data(report_id, **report_query)

    else:
        raise ValueError(f"Unsupported query type: {report_query['type']}")

    report_data['type'] = report_query['type']
    report_data['query'] = report.query if report_id else query.urlencode()

    return report_data


def get_student_ids_for_group_and_id(group, object_id, staff,
                                     return_set=True):
    """
    Takes an object of type Student, Section, grade_level, or Site, and returns
    the students associated with that object
    :return: List[int<student_ids>]
    """
    if group_is_model(group, "student"):
        return [object_id]

    if group_is_model(group, "grade_level"):
        site_id = staff.get_current_site_id()
        return GradeLevel.objects.get(pk=object_id) \
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

    group = query_params["group"]
    group_id = query_params["group_id"]
    site_id = query_params.get("site_id", None)
    staff = query_params.get("staff", None)

    student_ids = get_student_ids_for_group_and_id(group, group_id, staff)

    group_name = get_object_from_group_and_id(group, group_id)
    data = {
        "title": f"Attendance: {group_name}",
        "group": group,
        "group_id": group_id,
        "columns": AttendanceFlag.get_flag_columns(),  # can we cache somehow?
    }

    data["data"] = AttendanceDailyRecord.get_summaries_for_students(
        student_ids
    )

    if report_id:
        data["id"] = report_id

    return data


def grades_query_to_data(report_id=None, **query_params):
    """Currently supports getting most up to date data for grade"""

    group = query_params["group"]
    group_id = query_params["group_id"]
    course_id = query_params.get("course_id", None)
    category_id = query_params.get("category_id", None)
    staff = query_params.get("staff", None)

    student_ids = get_student_ids_for_group_and_id(group, group_id, staff)

    def _get_all_recent_course_grades_for_student_id(student_id):
        # Get all active sections for student
        now = timezone.now()
        end = timezone.datetime(2016, 6, 1)
        active_section_ids = (SectionLevelRosterPerYear.objects
                              .filter(student_id=student_id)
                              .filter(entry_date__lte=now, leave_date__gte=end)
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

        category_ids = []

        for gid in gradebook_ids:
            category_ids += (Gradebook.objects
                .get(id=gid)
                .category_set
                .values_list('id', flat=True))

        return (CategoryScoreCache.objects
                .filter(student_id=student_id)
                .filter(gradebook_id__in=gradebook_ids)
                .filter(category_id__in=category_ids)
                .exclude(possible_points__isnull=True)
                .order_by('category_id', '-calculated_at')
                .distinct('category_id')
                .all()
                )

    def _get_most_recent_assignment_grades(student_id, category_id):
        return (ScoreCache.objects
                .filter(student_id=student_id, category_id=category_id)
                .filter(assignment__is_active=True)
                .order_by('assignment_id', '-calculated_at')
                .distinct('assignment_id')
                .all()
                )

    def _calculate_gpa_from_grade_list(osc_list):
        if len(osc_list) == 0:
            return "NA"
        gpas = [GRADE_TO_GPA_POINTS[osc.mark.strip()] for osc in osc_list]
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
            "depth": "student",
            "label": label,
            "measures": [
                {"measure_label": "GPA", "measure": gpa, "primary": True}],
            "calculated_at": calculated_at,
            "children": [_shape_student_grades(o) for o in osc_list]
        }

        return shape

    def _shape_student_grades(overall_score_cache, children=False):
        osc = overall_score_cache
        course = (GradebookSectionCourseAffinity.objects
                  .filter(gradebook_id=osc.gradebook_id)
                  .order_by('-modified')
                  .first()
                  .course)

        shape = {
            "id": course.id,
            "depth": "course",
            "label": str(course),
            "measures": [
                {"measure_label": "Mark", "measure": osc.mark},
                {
                    "measure_label": "Percentage",
                    "measure": f"{osc.percentage}%" if osc.percentage else None,
                    "primary": True,
                },
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

    def _shape_category_grades(category_score_cache, children=False):
        csc = category_score_cache

        shape = {
            "id": csc.category_id,
            "depth": "category",
            "label": csc.category_name,
            "measures": [
                {
                    "measure_label": "Mark",
                    "measure": csc.mark
                },
                {
                    "measure_label": "Percentage",
                    "measure": f"{csc.percentage}%" if csc.percentage else None,
                    "primary": True,
                },
                {
                    "measure_label": "Missing Assignments",
                    "measure": csc.missing_count
                },
                # {"measure_label": "Weight", "measure": csc.weight}
            ],
            "calculated_at": csc.calculated_at
        }

        if children:
            assignment_grades = _get_most_recent_assignment_grades(
                csc.student_id, csc.category_id
            )
            shape["children"] = [_shape_assignment_grades(sc)
                                 for sc in assignment_grades]
        return shape

    def _shape_assignment_grades(score_cache):
        sc = score_cache

        shape = {
            "id": sc.assignment_id,
            "depth": "assignment",
            "label": str(sc.assignment),
            "measures": [
                {
                    "measure_label": "Points",
                    "measure": sc.points
                },
                {
                    "measure_label": "Percentage",
                    "measure": f"{sc.percentage}%" if sc.percentage else None,
                    "primary": True,
                },
                # {"measure_label": "Missing", "measure": sc.is_missing}
            ],
            "calculated_at": sc.calculated_at
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
    # Params: group, group_id, type (grades)
    # Constituent part: GPAs
    if group != "student":
        data = [_get_all_recent_course_grades_for_student_id(sid)
                for sid in student_ids]
        # filter out empty data sets
        formatted_data = [_shape_group_gpas(i) for i in data if len(i) > 0]
        title_string = f"Academic grades for {group_name} (latest)"

    # Individual student grades - all course grades
    # Params: group (student), group_id (student_id), type (grades)
    # Constituent parts: Course marks and percentages
    elif group == "student" and not (course_id or category_id):
        data = _get_all_recent_course_grades_for_student_id(group_id)
        formatted_data = [_shape_student_grades(i, children=True) for i in data]
        title_string = f"Academic grades for {group_name} (latest)"

    # Individual student grades - single course
    # Params: group (student), group_id (student_id), type (grades), course_id
    # Constituent parts: Category grades
    elif course_id and not category_id:
        data = _get_most_recent_category_grades(group_id, course_id)
        formatted_data = [_shape_category_grades(d, children=True) for d in
                          data]
        course_name = Course.objects.get(pk=course_id).short_name
        title_string = f"{course_name} grades for {group_name} (latest)"

    # Individual student grades - single course - single category
    # Params: group (student), group_id (student_id), type (grades),
    #         course_id, category_id
    # Constituent parts: Assignment grades
    else:
        data = _get_most_recent_assignment_grades(group_id, category_id)
        formatted_data = [_shape_assignment_grades(sc) for sc in data]
        course_name = Course.objects.get(pk=course_id).short_name
        category_name = Category.objects.get(pk=category_id).category_name
        title_string = f"{group_name}'s grades for " + \
                       f"{course_name}: {category_name}"

    response = {
        "title": title_string,
        "group": group,
        "group_id": group_id,
        "data": formatted_data
    }

    if report_id:
        response["id"] = report_id

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
