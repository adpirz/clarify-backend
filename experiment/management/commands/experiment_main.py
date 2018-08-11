from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Max, Min, Q, Sum
from tqdm import tqdm

from experiment.models import StudentWeekCategoryScore
from sis_mirror.models import Categories, Scores, GradingPeriods, \
    SectionTeacherAff, SectionGradingPeriodAff, GradebookSectionCourseAff, \
    SectionStudentAff, Assignments, Gradebooks

DATE_FORMAT = '%Y-%m-%d'


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            help="Specify which tables to update.",
        )

    def handle(self, *args, **options):
        # get a user_id
        user_id = int(options["user_id"])

        grading_periods = (
            GradingPeriods.objects
                .filter(grading_period_start_date__gte='2017-07-31',
                        grading_period_start_date__lte='2017-09-01')
                .values_list('grading_period_id', flat=True)
        )

        # import pdb;pdb.set_trace()
        start_date, week_end_dates = self\
            .get_end_dates_from_grading_period_ids(grading_periods)

        timespans = [(start_date, w) for w in week_end_dates]
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

        for span in timespans:
            start, end = span
            s = (Scores.objects.filter(
                gradebook_id__in=gbs,
                created__gte=start,
                created__lte=end)
                .values('student_id', 'assignment__category_id')
                .annotate(
                poss_points=Sum('assignment__possible_points'),
                total_points=Sum('value')
            ))

    @staticmethod
    def calculate_student_scores_for_week(student_id,
        # ...for each week, calculate scores, and put into table
                                          gradebook_ids,
                                          week_end_date):

        # Get all associated categories for gradebook
        categories = (Categories.objects
                      .filter(gradebook_id__in=gradebook_ids)
                      .all())

        # Get all assignments from grading period start up until end of week
        assignment_scores = Scores.objects.filter(
            created__lte=week_end_date,
            student_id=student_id,
            gradebook_id__in=gradebook_ids
        )

        # Calculate category scores
        def _calculate_category_score(category_id):
            """Returns ( total, possible )"""
            possible_points = 0
            total_points = 0
            category_scores = assignment_scores.filter(
                assignment__category_id=category_id
            ).all()

            for score in tqdm(category_scores, desc="{}: {} scores"\
                    .format(student_id, 'category ' + str(category_id))):
                total_points += score.value
                possible_points += score.assignment.possible_points

            return total_points, possible_points

        def _get_missing_count_for_category(category_id):
            assignments_turned_in = assignment_scores.values_list(
                'assignment_id', flat=True
            )

            assignments_due = Assignments.objects.filter(
                category_id=category_id,
                due_date__lte=week_end_date
            ).distinct('assignment_id').values_list('assignment_id', flat=True)

            return len([i for i in assignments_due
                        if i not in assignments_turned_in])

        def _calculate_total_gradebook_score():
            score_dict = {}
            for category in categories:
                score_dict[category.pk] = _calculate_category_score(category.pk)

            total = 0
            possible_points = 0
            total_weights = categories.aggregate(Sum('weight'))["weight__sum"]

            for cat_id, score_tuple in score_dict.items():
                weight = Categories.objects.get(pk=cat_id).weight / total_weights
                total += score_tuple[0] * weight
                possible_points += score_tuple[1] * weight

            return total, possible_points

        return _calculate_total_gradebook_score()


    @staticmethod
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

        return start, date_list
