from django.core.management.base import BaseCommand

from deltas.tasks import build_deltas_for_all_current_academic_teachers


class Command(BaseCommand):
    help = "Build all missing assignment deltas."

    def add_arguments(self, parser):
        parser.add_argument('--clean',
                            action='store_true',
                            dest='clean')

    def handle(self, *args, **options):
        success_string = build_deltas_for_all_current_academic_teachers(
            clean=True if options["clean"] else False
        )
        self.stdout.write(self.style.SUCCESS(success_string))