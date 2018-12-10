from datetime import datetime
from django.db import IntegrityError
from django.db.models import Sum, F, Avg, Max, Q, IntegerField, When, \
    Case, Count, FloatField, QuerySet
from django.utils import timezone
from pprint import pprint
from tqdm import tqdm

from clarify.models import Score, Assignment, Gradebook, Category
from sis_mirror.models import (
    ScoreCache,
    Users)
from .models import Delta, MissingAssignmentRecord, CategoryGradeContextRecord

tqdm.monitor_interval = 0


def get_missing_for_gradebook(gradebook_id):
    """Returns list of missing assignment objects for gradebook"""

    return (Score.objects
            .filter(assignment__gradebook_id=gradebook_id,
                    is_missing=True)
            .annotate(gradebook_id=F('assignment__gradebook_id'))
            .values('student_id', 'gradebook_id', 'assignment_id'))


def calculate_class_average_for_category(
        category_id, score: Score = None, datetime: datetime = None):
    """Calculate class average, optionally up until a certain date or score"""

    end_date = None

    if datetime:
        end_date = datetime.date()
    elif score:
        end_date = score.last_updated.date()

    arg_filters = []
    kwarg_filters = {
        "assignment__category_id": category_id,
    }

    if end_date:
        kwarg_filters["last_updated__date__lte"] = end_date
        arg_filters += [Q(assignment__due_date__lte=end_date) |
                        Q(assignment__due_date__isnull=True)]

    return {**(
        Score.objects
            .filter(*arg_filters, **kwarg_filters)
            .exclude(is_excused=True,
                     points__isnull=True)
            .values('student_id')
            .annotate(
                total_points=Sum('points'),
                total_possible_points=Sum('assignment__possible_points'),
                latest=Max(F('last_updated'))
            )
            .aggregate(
                total_points_possible=Max(F('total_possible_points')),
                average_points_earned=Avg(F('total_points')),
                date=Max(F('latest'))
            )
            ), **{'category_id': category_id}}


def calculate_category_scores_until_date_or_score(
        student_id_or_ids=None, category_id_or_ids=None,
        date: datetime = None, score: ScoreCache = None,
        **extra_score_cache_filters):
    """Returns the category scores for each"""
    if not student_id_or_ids and not category_id_or_ids:
        raise ValueError("Need either student_ids or category_ids.")

    if not date and not score:
        end_date = timezone.now().date()
    else:
        end_date = date if date else score.last_updated

    if isinstance(student_id_or_ids, int):
        student_filter = {"student_id": student_id_or_ids}
    elif isinstance(student_id_or_ids, list) or isinstance(student_id_or_ids, QuerySet):
        student_filter = {"student_id__in": student_id_or_ids}
    elif student_id_or_ids is None:
        student_filter = {}
    else:
        raise TypeError("Param 'student_id' must be int or list, "
                        f"got type {type(student_id_or_ids)}")

    if isinstance(category_id_or_ids, int):
        category_filter = {"assignment__category_id": category_id_or_ids}
    elif isinstance(category_id_or_ids, list):
        category_filter = {"assignment__category_id__in": category_id_or_ids}
    elif category_id_or_ids is None:
        category_filter = {}
    else:
        raise TypeError("Param 'category_id' must be int or list, "
                        f"got type {type(category_id_or_ids)}")

    if student_id_or_ids is not None:
        values_list = ['student_id']
    else:
        values_list = []

    return (
        Score.objects
            .filter(**{
                **student_filter,
                **category_filter,
                **extra_score_cache_filters
            })
            .filter(
                Q(assignment__due_date__lte=end_date) |
                Q(assignment__due_date__isnull=True),
                assignment__is_active=True,
                last_updated__lte=end_date)
            .prefetch_related('assignment__category')
            .values(*values_list,
                    category_id=F('assignment__category_id'),
                    category_name=F('assignment__category__name'))
            .annotate(
                assignment_count=Count('assignment_id', distinct=True),
                points_earned=Sum('points'),
                possible_points=Sum(Case(When(points__isnull=True, then=0),
                                    default=F('assignment__possible_points')),
                                    output_field=FloatField()),
                excused_count=Sum(Case(When(is_excused=True, then=1), default=0),
                                  output_field=IntegerField()),
                missing_count=Sum(Case(When(is_missing=True, then=1), default=0),
                                  output_field=IntegerField())
            )
            .order_by(*(values_list + ['category_id'])
        )
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

    gradebooks = Gradebook\
        .get_all_current_gradebook_ids_for_user_profile(user_id)

    missing = []

    for gradebook_id in tqdm(gradebooks,
                          desc="Gradebooks",
                          leave=False):
        missing += get_missing_for_gradebook(gradebook_id)

    student_dict = {}

    for missing_assignment in missing:
        student_id = missing_assignment["student_id"]
        if student_id not in student_dict:
            student_dict[student_id] = []
        student_dict[student_id].append(missing_assignment)

    return student_dict


def delta_threshold_test(score: Score, running_score_dict):
    """
    Threshold test for creating a delta
    :param score: Current score to test (not included in running_score_dict)
    :param running_score_dict: Points in category so far;
        { total_earned, total_possible }
    :return: bool
    """
    # TODO: create a better test for score thresholds

    total_earned = running_score_dict['points_earned']
    total_possible = running_score_dict['possible_points']

    if total_possible == 0:
        raise ValueError("Running score has no possible points, " +
                         "should have at least " +
                         f"{score.assignment.possible_points}")

    before_percentage = total_earned / total_possible

    clean_score = score.score or 0

    after_earned = total_earned + clean_score

    after_possible = total_possible + score.assignment.possible_points
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
        .annotate(score_created=F('score__last_updated'))
        .first()
    )

    scores_filter = {
        'student_id': student_id,
        'assignment__category_id': category_id
    }

    if latest_delta:
        scores_filter["last_updated__gt"] = latest_delta.score_created

    scores_list = (
        Score.objects
        .filter(**scores_filter)
        .exclude(is_excused=True)
        .exclude(points__isnull=True,
                 assignment__possible_points__isnull=True)
        .order_by('assignment__due_date')
        .prefetch_related('assignment', 'delta_set')
        .all()
    )

    if latest_delta:
        running_total = \
            calculate_category_scores_until_date_or_score(
                student_id, category_id, latest_delta.score_created)[0]
    else:
        running_total = {
            'points_earned': 0.0,
            'possible_points': 0.0
        }

    new_deltas = 0

    for score in scores_list:

        if score.delta_set.exists():
            continue

        try:
            points_earned = running_total["points_earned"]
            possible_points = running_total["possible_points"]
        except TypeError:
            import pdb; pdb.set_trace()

        # if score.points is null or assignment has null possible points,
        # we don't want to measure for a delta or running total
        if score.points is None or score.assignment.possible_points is None:
            continue

        # check if there exists any delta at the tail
        # or if at the current point, we cross the threshold

        if running_total["possible_points"] == 0 or \
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
                data = calculate_class_average_for_category(
                    category_id, score)
                data["category_id"] = category_id
                try:
                    category_context = (
                        CategoryGradeContextRecord.objects.create(**data)
                    )
                except IntegrityError:
                    pprint(data)
                    import pdb; pdb.set_trace()
                    continue
            try:
                category_average_before = 0 if possible_points == 0 \
                    else points_earned / possible_points

                after_earned = points_earned + score.points
                after_possible = possible_points + \
                    score.assignment.possible_points

                category_average_after = after_earned / after_possible

            except TypeError:
                import pdb
                pdb.set_trace()

            # TODO: speed up 'score' queries by returning only needed vals
            Delta.objects.create(
                type='category',
                student_id=student_id,
                context_record=category_context,
                score=score,
                gradebook_id=score.assignment.gradebook_id,
                category_average_before=category_average_before,
                category_average_after=category_average_after
            )

            new_deltas += 1

        # keep the running total going no matter what

        running_total['points_earned'] += score.points
        running_total['possible_points'] += score.assignment.possible_points

    return new_deltas


def build_deltas_for_category(category_id):
    student_ids = (
        Score.objects
        .filter(assignment__category_id=category_id)
        .distinct('student_id')
        .values_list('student_id', flat=True)
    )

    new_deltas = 0
    for student_id in tqdm(student_ids, desc="Students", leave=False):
        new_deltas += \
            build_deltas_for_student_and_category(student_id, category_id)

    return new_deltas


def build_deltas_for_gradebook(gradebook_id):
    category_ids = (Category.objects
                    .filter(gradebook_id=gradebook_id)
                    .values_list('id', flat=True))

    new_deltas = 0

    for category_id in tqdm(category_ids, desc="Categories", leave=False):
        new_deltas += build_deltas_for_category(category_id)

    return new_deltas


def build_deltas_for_staff_current_gradebooks(staff_id):
    gradebook_ids = Gradebook.get_all_current_gradebook_ids_for_user_profile(staff_id)

    new_deltas = 0

    for gradebook_id in tqdm(gradebook_ids, desc="Gradebooks", leave=False):
        new_deltas += build_deltas_for_gradebook(gradebook_id)

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
            clarify_gradebook = Gradebook.objects.get(
                id=missing_assignments[0]['gradebook_id']
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
            import pdb
            pdb.set_trace()
            raise e

        for assignment in missing_assignments:
            clarify_assignment = Assignment.objects.get(
                id=assignment["assignment_id"]
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
        new_missing_deltas, errors = build_missing_assignment_deltas_for_user(
            teacher_id)
        new_category_deltas = build_deltas_for_staff_current_gradebooks(
            teacher_id)

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
