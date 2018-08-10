from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Max, Min, Q, Sum
from tqdm import tqdm

from experiment.models import StudentWeekCategoryScore
from sis_mirror.models import Categories, Scores, GradingPeriods, \
    SectionTeacherAff, SectionGradingPeriodAff, GradebookSectionCourseAff, \
    SectionStudentAff, Assignments

DATE_FORMAT = '%Y-%m-%d'


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            help="Specify which tables to update.",
        )

    def handle(self, *args, **options):
        between_date = options.get('start_date', '2017-09-01')

        # get a user_id
        user_id = int(options["user_id"])

        # ...get all grading periods within a timeframe...
        grading_periods = GradingPeriods.objects.filter(
            grading_period_start_date__lte=between_date,
            grading_period_end_date__gte=between_date
        ).values_list('grading_period_id', flat=True)

        # for each gradebook associated within a grading period...
        teacher_sections = (SectionTeacherAff
                            .objects
                            .filter(user_id=user_id)
                            .values_list('section_id', flat=True))

        sections_in_grading_period = (
            SectionGradingPeriodAff.objects
                .filter(grading_period_id__in=grading_periods)
                .filter(section_id__in=teacher_sections)
                .values_list('section_id', flat=True)
        )

        gbs_from_sections = (
                GradebookSectionCourseAff.objects
                .filter(section_id__in=sections_in_grading_period)
                .values_list('gradebook_id', flat=True)
        )

        # ...build out end dates for each week from grading_periods...
        week_dates = self.get_end_dates_from_grading_period_ids(grading_periods)

        for week_end_date in tqdm(week_dates, desc="Week Dates"):
            students = SectionStudentAff.objects.filter(
                section_id__in=sections_in_grading_period,
                entry_date__lte=week_end_date,
            ).filter(
                Q(leave_date__gte=week_end_date) | Q(leave_date__isnull=True)
            )
            for student in tqdm(students, desc="Students"):
                print(self.calculate_student_scores_for_week(
                    student.student_id, gbs_from_sections, week_end_date
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

        return date_list
