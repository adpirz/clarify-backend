from django.db import IntegrityError
from django.utils import timezone
from tqdm import tqdm

from sis_mirror.models import (
    Gradebooks,
    GradingPeriods,
    ScoreCache,
    SsCube)

from .models import Delta, MissingAssignmentRecord


def get_missing_for_gradebook(gradebook_id):
    """Returns list of missing assignment objects for gradebook"""

    missing = (
        ScoreCache.objects
            .filter(gradebook_id=gradebook_id, is_missing=True)
            .order_by('student_id', '-calculated_at')
            .distinct('student_id', 'assignment_id', 'calculated_at')
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

    for gradebook_id in tqdm(gradebook_ids,
                             desc="Gradebooks",
                             leave=False):
        missing += get_missing_for_gradebook(gradebook_id)

    student_dict = {}

    for missing_assignment in missing:
        student_id = missing_assignment['student_id']
        if not student_id in student_dict:
            student_dict[student_id] = []
        student_dict[student_id].append(missing_assignment)

    return student_dict


"""

    Missing Assignment Deltas:
    
    1. Pull missing assignments for a gradebook from ScoreCache
    2. For each student with missing assignments, create a delta 
    3. Check if delta is duplicate; if not, save
    
"""


def build_deltas_for_user(user_id, grading_period_id=None):

    # get all missing assignments by student
    all_missing = get_all_missing_for_user(user_id, grading_period_id)

    new_deltas_created = 0
    errors = 0

    for student_id, missing_assignments in tqdm(all_missing.items(),
                                                desc="Students",
                                                leave=False):
        last_missing_delta_for_student = (
            Delta.objects
                .filter(student_id=student_id,
                        type="missing",
                        gradebook_id=missing_assignments[0]["gradebook_id"])
                .order_by('-updated_on')
                .first()
        )

        # Check if a delta exists for this set
        if last_missing_delta_for_student:
            old_set = set(
                last_missing_delta_for_student
                    .missingassignmentrecord_set
                    .values_list('assignment_id', flat=True)
            )
            new_set = set([ma["assignment_id"] for ma in missing_assignments])

            if old_set == new_set:
                continue

        try:
            new_delta = Delta.objects.create(
                type="missing",
                student_id=student_id,
                gradebook_id=missing_assignments[0]['gradebook_id'],
            )
        except IntegrityError as e:
            print(f"Error creating delta: {e}")
            errors += 1

        for assignment in missing_assignments:
            try:
                MissingAssignmentRecord.objects.create(
                    delta=new_delta,
                    assignment_id=assignment["assignment_id"],
                    missing_on=timezone.now().date()
                )
            except IntegrityError:
                print(f"Error adding to delta: {e}")
                errors += 1

        new_deltas_created += 1

    return new_deltas_created, errors


def build_deltas_for_all_current_academic_teachers():
    teacher_ids = (
        SsCube.objects
            .distinct('user_id')
            .values_list('user_id', flat=True)
    )

    start = timezone.now()

    total_new_deltas = 0
    total_errors = 0

    for teacher_id in tqdm(teacher_ids, desc="Staff"):
        new_deltas, errors = build_deltas_for_user(teacher_id)
        total_new_deltas += new_deltas
        total_errors += errors

    end = timezone.now()

    return "Completed all missing assignment deltas for current teachers." + \
           f"\n\tTeachers: {len(teacher_ids)}" + \
           f"\n\tTotal new deltas: {total_new_deltas}" + \
           f"\n\tTotal errors: {total_errors}" + \
           f"\n\tTotal time elapsed (seconds): {(end - start).total_seconds()}"
