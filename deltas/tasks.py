from tqdm import tqdm

from sis_mirror.models import (
    Gradebooks,
    GradingPeriods,
    ScoreCache
)


def get_missing_for_gradebook(gradebook_id):
    """Returns list of missing assignment objects for gradebook"""

    missing = (
        ScoreCache.objects
            .filter(gradebook_id=gradebook_id, is_missing=True)
            .order_by('student_id')
            .values_list(
                'assignment_id', 'assignment__short_name',
                'student_id', 'student__first_name', 'student__last_name',
                'gradebook_id', 'gradebook__gradebook_name'
        )
    )

    def _shape(missing_tuple):
        a_id, a_sn, s_id, s_fn, s_ln, gb_id, gb_n = missing_tuple

        return {
            'assignment_id': a_id,
            'assignment_name': a_sn,
            'student_id': s_id,
            'student_first_name': s_fn,
            'student_last_name': s_ln,
            'gradebook_id': gb_id,
            'gradebook_name': gb_n
        }

    return [_shape(t) for t in missing]


def get_all_missing_for_user(user_id, grading_period_id=None):
    """
    Get all missing assignments for a teacher and gradebook
    Defaults to most recent active grading period.
    :param user_id: Illuminate user id
    """

    if grading_period_id:
        active_grading_periods = [grading_period_id]
    else:
        active_grading_periods = (
            GradingPeriods.get_all_current_grading_periods()
                .values_list('grading_period_id', flat=True)
        )

    grading_period_filter = "__".join([
        "gradebooksectioncourseaff",
        "section",
        "sectiongradingperiodaff",
        "grading_period_id",
        "in"
    ])
    gradebook_ids = (
        Gradebooks.objects
            .filter(**{grading_period_filter: active_grading_periods})
            .filter(created_by=user_id)
            .values_list('gradebook_id', flat=True)
    )

    missing = []

    for gradebook_id in gradebook_ids:
        missing += get_missing_for_gradebook(gradebook_id)

    student_dict = {}

    for missing_assignment in missing:
        student_id = missing_assignment[2]
        if not student_id in student_dict:
            student_dict[student_id] = []
        student_dict[student_id].append(missing_assignment)

    return student_dict


"""

    Missing Assignment Deltas:
    
    - Pull missing assignments for a gradebook from ScoreCache
    - For each student with missing assignments, create a delta 
    - C
    
"""


def build_deltas_for_user(user_id, grading_period_id=None):

    # get all missing assignments by student
    all_missing = get_all_missing_for_user(user_id, grading_period_id)

    for student_id, missing_assignments in tqdm(all_missing.items(),
                                                desc="Students"):
        # check if a record exists of all missing assignments
        assignment_ids = [ma["assignment_id"] for ma in missing_assignments]

