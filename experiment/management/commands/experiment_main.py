from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from sis_mirror.models import Categories, Scores, GradingPeriods, \
    SectionTeacherAff, SectionGradingPeriodAff, GradebookSectionCourseAff, \
    SectionStudentAff

DATE_FORMAT = '%Y-%m-%d'


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            help="Specify which tables to update.",
        )

    def handle(self, *args, **options):
        start_date_string = options.get('start_date', '2017-09-01')
        end_date_string = options.get('end_date', '2017-12-01')

        start_date, end_date = map(
            lambda d: datetime.strptime(d, DATE_FORMAT),
            (start_date_string, end_date_string)
        )

        # get a user_id
        user_id = int(options["user_id"])

        # ...get all grading periods within a timeframe...
        grading_periods = GradingPeriods.objects.filter(
            grading_period_start_date__lte=start_date,
            grading_period_end_date__gte=end_date
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

        # ...for each week, calculate scores, and put into table
        for week_end_date in week_dates:
            students = SectionStudentAff.objects.filter(
                section_id__in=sections_in_grading_period

            )




    @staticmethod
    def calculate_student_scores_for_week(student_id,
                                          gradebook_id,
                                          week_end_date):
        pass
        # Get all associated categories for gradebook
        categories = Categories.objects.filter(gradebook_id=gradebook_id)

        # Get all assignments from grading period start up until end of week
        category_assignment_scores = Scores.objects.filter(

        )

        # Calculate

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
