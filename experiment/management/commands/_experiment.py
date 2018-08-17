from datetime import timedelta
from tqdm import tqdm

from django.db import IntegrityError
from django.db.models import Min, Max, Sum, Count

from experiment.experiment_utils import get_all_users_for_set_dates
from experiment.models import StudentWeekCategoryScore
from sis_mirror.models import GradingPeriods, Gradebooks, Scores, Users


def main(self, *args, **options):
    handle_all_users(*args, **options)


def single_user(user_id, *args, **options):

    grading_periods = (
        GradingPeriods.objects
            .filter(grading_period_start_date__gte='2017-07-31',
                    grading_period_start_date__lte='2017-09-01')
            .values_list('grading_period_id', flat=True)
    )

    spans = get_end_dates_from_grading_period_ids(grading_periods)

    through_string = "__".join([
        "gradebooksectioncourseaff",
        "section",
        "sectiongradingperiodaff",
        "grading_period_id",
        "in"
    ])

    gb_filters = {
        through_string: grading_periods,
        "created_by": user_id
    }

    gbs = Gradebooks.objects.filter(**gb_filters).values_list(
        'gradebook_id', flat=True
    )
    scores = []
    for span in spans:
        start, end = map(lambda t: t.strftime('%Y-%m-%d'), span)
        s = (Scores.objects.filter(
            gradebook_id__in=gbs,
            created__gte=start,
            created__lte=end)
            .values('student_id',
                    'gradebook_id',
                    'gradebook__gradebook_name',
                    'gradebook__created_by_id',
                    'assignment__category__category_name',
                    'assignment__category__weight',
                    'assignment__category_id')
            .annotate(
            num_assignments=Count('assignment_id', distinct=True),
            poss_points=Sum('assignment__possible_points'),
            total_points=Sum('value')
        ).all())

        for i in s:
            total = 0 if not i['total_points'] else i['total_points']
            poss_points = 0 if not i['poss_points'] else i['poss_points']
            percentage = None if poss_points == 0 else float(total/poss_points)

            scores.append(
                StudentWeekCategoryScore(
                    student_id=i['student_id'],
                    possible_points=poss_points,
                    total_points=total,
                    percentage=percentage,
                    number_of_assignments=i['num_assignments'],
                    gradebook_id=i['gradebook_id'],
                    gradebook_name=i['gradebook__gradebook_name'],
                    user_id=i['gradebook__created_by_id'],
                    start_date=start,
                    end_date=end,
                    category_id=i['assignment__category_id'],
                    category_name=i['assignment__category__category_name'],
                    category_weight=i['assignment__category__weight']
                )
            )

    def save_individual():
        errors = 0
        for i in tqdm(scores, desc="Saving scores"):
            try:
                i.save()
            except IntegrityError as e:
                print("Error", e)
                errors += 1

        print(f"Total errors: {errors}\n")

    if options["no_bulk"]:
        save_individual()
    else:
        try:
            StudentWeekCategoryScore.objects.bulk_create(scores)
        except IntegrityError as e:
            print(e)
            print("Trying individually...")
            save_individual()


def handle_all_users(*args, **options):
    all_user_ids = get_all_users_for_set_dates()

    for u in tqdm(all_user_ids, desc="All users"):
        single_user(u, *args, **options)


def get_end_dates_from_grading_period_ids(grading_period_ids):
    gps = GradingPeriods.objects.filter(
        grading_period_id__in=grading_period_ids
    )

    aggs = gps.aggregate(
        Min('grading_period_start_date'),
        Max('grading_period_end_date')
    )

    start = aggs["grading_period_start_date__min"]
    end = aggs["grading_period_end_date__max"]

    # https://http://ajaiswal.net/python-find-all-the-dates-of-particular-week-days/

    tmp_list = list()
    date_list = list()

    # Creates a list of all the dates falling between end and start
    for x in range((end - start).days + 1):
        tmp_list.append(start + timedelta(days=x))
    for date_record in tmp_list:
        if date_record.weekday() == 6:
            date_list.append(date_record)

    out_list = [(start, date_list[0])] + \
               [(x, date_list[i-1]) for i, x in enumerate(date_list) if i > 0]
    return out_list
