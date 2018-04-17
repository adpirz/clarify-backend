from django.core.management.base import BaseCommand, CommandError
from sis_pull.tasks.main import main

class Command(BaseCommand):
    def handle(self, *args, **options):
        main()