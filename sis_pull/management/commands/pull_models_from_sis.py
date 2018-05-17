from django.core.management.base import BaseCommand, CommandError
from sis_pull.tasks.main import main, clean_all


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            'models',
            nargs='*',
            help="Specify which tables to update."
        )

        parser.add_argument(
            '--clean',
            dest='clean',
            action='store_true',
            help='Delete models before updating.'
        )

        parser.add_argument(
            '--no-bulk',
            dest='no_bulk',
            action='store_true',
            help='Force all models to insert row by row instead of bulk.'
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Deleting current models before updating...')
        models_run = main(**options)
        self.stdout.write(
            self.style.SUCCESS('Complete. Models run: {}'
                               .format(', '.join(models_run))))
