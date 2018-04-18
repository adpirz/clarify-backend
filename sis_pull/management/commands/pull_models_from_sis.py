from django.core.management.base import BaseCommand, CommandError
from sis_pull.tasks.main import main, delete_all


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-all',
            action='store_true',
            dest='delete',
            help='Delete all models before pulling SIS models.',
        )

    def handle(self, *args, **options):
        if options['delete']:
            delete_all()
        main()