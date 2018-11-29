from datetime import datetime

from django.db import IntegrityError
from django.db.models import Sum, F, Avg, Max, Q, Count
from django.utils import timezone
from tqdm import tqdm

from clarify.models import Score, Assignment, Gradebook, Student
from sis_mirror.models import (
    Gradebooks,
    GradingPeriods,
    SsCube,
    ScoreCache,
    Categories,
    Users)

from .models import Delta, MissingAssignmentRecord, CategoryGradeContextRecord


tqdm.monitor_interval = 0


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
        ).prefetch_related('assignment', 'student', 'gradebook')
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


def calculate_class_average_for_category(
        category_id, score: ScoreCache=None, datetime: datetime=None):
    """Calculate class average, optionally up until a certain date or score"""

    end_date = None

    if datetime:
        end_date = datetime.date()
    elif score:
        end_date = score.last_updated.date()

    filters = {
        "category_id": category_id,
    }
    if end_date:
        filters["last_updated__date__lte"] = end_date
        filters["assignment__due_date__lte"] = end_date

    return {**(
        ScoreCache.objects
            .filter(**filters)
            .exclude(is_excused=True)
            .exclude(points__isnull=True)
            .exclude(points=0.0)
            .values('student_id')
            .annotate(
                total_points=Sum('score'),
                total_possible_points=Sum('assignment__possible_points'),
                latest=Max(F('last_updated'))
            )
            .aggregate(
                total_points_possible=Max(F('total_possible_points')),
                average_points_earned=Avg(F('total_points')),
                date=Max(F('latest'))
                )
            )
            , **{'category_id': category_id}}


def calculate_category_score_until_date_or_score_for_student(
        student_id, category_id, date: datetime=None, score: ScoreCache=None):
    """Returns the category scores for each """

    if not date and not score:
        raise ValueError("Must have a date or score.")

    end_date = date if date else score.last_updated

    return (
        ScoreCache.objects
            .filter(student_id=student_id, category_id=category_id)
            .filter(assignment__due_date__lte=end_date,
                    last_updated__lte=end_date)
            .exclude(points__isnull=True)
            .prefetch_related('category')
            .values('student_id',
                    'gradebook_id',
                    category_id=F('category_id'),
                    category_name=F('category__category_name'))
            .annotate(total_earned=Sum('score'))
            .annotate(total_possible=Sum('assignment__possible_points'))
            .annotate(assignment_count=Count('assignment_id'))
            .all()[0]
    )


def get_scores_until_date_for_student(student_id, gradebook_id, date):

    return (
        ScoreCache.objects
            .filter(student_id=student_id, gradebook_id=gradebook_id)
            .filter(assignment__due_date__lte=date, last_updated__lte=date)
            .exclude(is_excused=True)
            .exclude(points__isnull=True)
            .exclude(points=0.0)
            .prefetch_related(
                'assignment', 'assignment__category', 'gradebook')
            .values('student_id',
                    'score',
                    'gradebook_id',
                    'assignment_id',
                    gradebook_name=F('gradebook_name'),
                    due_date=F('assignment__due_date'),
                    assign_date=F('assignment__assign_date'),
                    assignment_name=F('assignment__short_name'),
                    possible_points=F('points'))
            .all()
    )


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
    gradebooks = Gradebooks.get_current_gradebooks_for_staff_id(user_id)

    missing = []

    for gradebook in tqdm(gradebooks,
                             desc="Gradebooks",
                             leave=False):
        missing += get_missing_for_gradebook(gradebook["sis_id"])

    student_dict = {}

    for missing_assignment in missing:
        student_id = missing_assignment['student_id']
        if not student_id in student_dict:
            student_dict[student_id] = []
        student_dict[student_id].append(missing_assignment)

    return student_dict


def delta_threshold_test(score: ScoreCache, running_score_dict):
    """
    Threshold test for creating a delta
    :param score: Current score to test (not included in running_score_dict)
    :param running_score_dict: Points in category so far;
        { total_earned, total_possible }
    :return: bool
    """
    # TODO: create a better test for score thresholds

    total_earned = running_score_dict['total_earned']
    total_possible = running_score_dict['total_possible']

    if total_possible == 0:
        raise ValueError("Running score has no possible points, " + \
                         "should have at least " + \
                         f"{score.assignment.possible_points}")

    before_percentage = total_earned / total_possible

    clean_score = score.score or 0

    after_earned = total_earned + clean_score
    after_possible = total_possible + score.points
    after_percentage = after_earned / after_possible

    if abs(after_percentage - before_percentage) > 0.1:
        return True

    return False


def build_deltas_for_student_and_category(student_id, category_id):

    latest_delta = (
        Delta.objects
            .filter(type="category",
                    student_id=student_id,
                    score__assignment__category_id=category_id)
            .prefetch_related('score')
            .order_by('-updated_on')
            .annotate(score_created=F('score__updated_on'))
            .first()
    )

    scores_filter = {
        'student_id': student_id,
        'assignment__category_id': category_id
    }

    if latest_delta:
        scores_filter["updated_on__gt"] = latest_delta.score_created

    scores_list = (
        Score.objects
            .filter(**scores_filter)
            .exclude(is_excused=True)
            .exclude(score__isnull=True,
                     assignment__possible_points__isnull=True)
            .order_by('assignment__due_date')
            .prefetch_related('assignment', 'delta_set')
            .all()
    )

    if latest_delta:
        running_total = calculate_category_score_until_date_or_score_for_student(
            student_id, category_id, latest_delta.score_created
        )
    else:
        running_total = {
            'total_earned': 0.0,
            'total_possible': 0.0
        }

    new_deltas = 0

    for score in scores_list:
        if score.delta_set.exists():
            continue

        total_earned = running_total["total_earned"]
        total_possible = running_total["total_possible"]

        if not (isinstance(score.score, int) or isinstance(score.score, float))\
                and not (isinstance(score.assignment.possible_points, int) or
                         isinstance(score.assignment.possible_points, float)):
            continue

        clean_score = score.score or 0

        if running_total["total_possible"] == 0 or \
           delta_threshold_test(score, running_total):

            try:
                category_context = (
                    CategoryGradeContextRecord.objects
                        .get(
                            date=score.last_updated.date(),
                            category_id=category_id
                    )
                )

            except CategoryGradeContextRecord.DoesNotExist:
                data = calculate_class_average_for_category(category_id, score)
                category_context = (
                    CategoryGradeContextRecord.objects.create(**data)
                )

            category_average_before = 0 if total_possible == 0 \
                else total_earned / total_possible

            after_earned = total_earned + clean_score
            after_possible = total_possible + score.assignment.possible_points

            category_average_after = after_earned / after_possible

            Delta.objects.create(
                type='category',
                student_id=student_id,
                context_record=category_context,
                score=score,
                gradebook_id=score.gradebook_id,
                category_average_before=category_average_before,
                category_average_after=category_average_after
            )

            new_deltas += 1

        running_total['total_earned'] += clean_score
        running_total['total_possible'] += score.points

    return new_deltas


def build_deltas_for_category(category_id):
    student_ids = (
        ScoreCache.objects
            .filter(category_id=category_id)
            .distinct('student_id')
            .values_list('student_id', flat=True)
    )

    new_deltas = 0
    for student_id in tqdm(student_ids, desc="Students", leave=False):
        new_deltas += \
            build_deltas_for_student_and_category(student_id, category_id)

    return new_deltas


def build_deltas_for_gradebook(gradebook_id):
    category_ids = (
        Categories.objects
            .filter(gradebook_id=gradebook_id)
            .distinct('category_id')
            .annotate(id=F('category_id'))
            .values_list('id', flat=True)
    )

    new_deltas = 0

    for category_id in tqdm(category_ids, desc="Categories", leave=False):
        new_deltas += build_deltas_for_category(category_id)

    return new_deltas


def build_deltas_for_staff_current_gradebooks(staff_id):
    gradebooks = Gradebooks.get_current_gradebooks_for_staff_id(staff_id)

    new_deltas = 0

    for gradebook in tqdm(gradebooks, desc="Gradebooks", leave=False):
        new_deltas += build_deltas_for_gradebook(gradebook["sis_id"])

    return new_deltas

"""

    Missing Assignment Deltas:

    1. Pull missing assignments for a gradebook from ScoreCache
    2. For each student with missing assignments, create a delta
    3. Check if delta is duplicate; if not, save

"""


def build_missing_assignment_deltas_for_user(user_id, grading_period_id=None):

    # get all missing assignments by student
    all_missing = get_all_missing_for_user(user_id, grading_period_id)

    new_deltas_created = 0
    errors = 0

    for sis_student_id, missing_assignments in tqdm(all_missing.items(),
                                                desc="Students",
                                                leave=False):
        student_id = Student.objects.get(sis_id=sis_student_id).id

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
            clarify_gradebook = Gradebook.objects.get(
                sis_id=missing_assignments[0]['gradebook_id']
            )
            new_delta = Delta.objects.create(
                type="missing",
                student_id=student_id,
                gradebook_id=clarify_gradebook.id,
            )

        except IntegrityError as e:
            print(f"Error creating delta: {e}")
            errors += 1
            continue
        except Exception as e:
            import pdb; pdb.set_trace()
            raise e

        for assignment in missing_assignments:
            clarify_assignment = Assignment.objects.get(
                sis_id=assignment["assignment_id"]
            )

            try:
                MissingAssignmentRecord.objects.create(
                    delta=new_delta,
                    assignment_id=clarify_assignment.id,
                    missing_on=timezone.now().date()
                )
            except IntegrityError:
                print(f"Error adding to delta: {e}")
                errors += 1

        new_deltas_created += 1

    return new_deltas_created, errors


def build_deltas_for_all_current_academic_teachers(clean=False):

    if clean:
        Delta.objects.all().delete()

    teacher_ids = Users.get_all_current_staff_ids()

    start = timezone.now()

    missing_deltas = 0
    category_deltas = 0
    total_errors = 0

    for teacher_id in tqdm(teacher_ids, desc="Staff"):
        new_missing_deltas, errors = build_missing_assignment_deltas_for_user(teacher_id)
        new_category_deltas = build_deltas_for_staff_current_gradebooks(teacher_id)

        missing_deltas += new_missing_deltas
        category_deltas += new_category_deltas
        total_errors += errors

    total_new_deltas = missing_deltas + category_deltas
    end = timezone.now()
    minutes, seconds = divmod(round((end - start).total_seconds()), 60)

    success_string = "Completed all missing assignment and category " + \
        "deltas for current teachers." + \
        f"\n\tTeachers: {len(teacher_ids)}" + \
        f"\n\tTotal new deltas: {total_new_deltas} | " + \
        f"Missing: {missing_deltas} | " + \
        f"Category: {category_deltas}" + \
        f"\n\tTotal errors: {total_errors}" + \
        f"\n\tTotal time elapsed: {minutes} min {seconds} sec"

    if clean:
        success_string = "[ Cleaned: all prior deltas deleted ]\n" + \
                         success_string

    return success_string
