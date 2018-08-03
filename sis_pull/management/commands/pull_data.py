import time
from subprocess import call

from django.core.management.base import BaseCommand, CommandError
from sis_pull.tasks.main import main


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

        parser.add_argument(
            '--createsuperuser',
            dest='superuser',
            action='store_true',
            help='Create superuser. Will create after clean insert.'
        )

    def handle(self, *args, **options):
        superuser = False
        if options['clean']:
            self.stdout.write('Deleting current models before updating...')
        start = time.time()

        # CENTRAL METHOD
        models_run = main(**options)

        end = time.time()

        if 'users' in models_run:
            options['superuser'] = True

        if options['superuser']:
            process_exit = call(['python', 'manage.py', 'createsuperuser'])
            superuser = True if process_exit == 0 else False

        output = 'Completed in {} seconds. Models run: {}'.format(
            round(end - start, 1), ', '.join(models_run))

        if superuser:
            output += '\nSuperuser created.'

        self.stdout.write(self.style.SUCCESS(output))
