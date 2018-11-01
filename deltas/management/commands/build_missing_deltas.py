from django.core.management.base import BaseCommand

from deltas.tasks import build_deltas_for_all_current_academic_teachers


class Command(BaseCommand):
    help = "Build all missing assignment deltas."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        success_string = build_deltas_for_all_current_academic_teachers()
        self.stdout.write(self.style.SUCCESS(success_string))