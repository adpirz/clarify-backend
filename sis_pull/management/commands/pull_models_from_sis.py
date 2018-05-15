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

    def handle(self, *args, **options):
        models_run = main(**options)
        if options['clean']:
            self.stdout.write('Deleting current models before updating...')
        self.stdout.write(
            self.style.SUCCESS('Complete. Models run: {}'
                               .format(', '.join(models_run))))
