from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Max, Min, Q, Sum
from tqdm import tqdm

from experiment.models import StudentWeekCategoryScore
from sis_mirror.models import Categories, Scores, GradingPeriods, \
    SectionTeacherAff, SectionGradingPeriodAff, GradebookSectionCourseAff, \
    SectionStudentAff, Assignments, Gradebooks

from ._experiment import main

DATE_FORMAT = '%Y-%m-%d'


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):

        parser.add_argument('--no_bulk',
                            action='store_true',
                            dest='no_bulk',
                            )

        parser.add_argument('--clean',
                            action='store_true',
                            dest='clean')
        
    def handle(self, *args, **options):
        if options["clean"]:
            print("Deleting all StudentWeekCategoryScore instances...")
            print(StudentWeekCategoryScore.objects.all().delete())

        main(self, *args, **options)