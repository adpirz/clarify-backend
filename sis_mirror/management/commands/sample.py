from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        db_conn = connections['clarifycache']
        try:
            c = db_conn.cursor()
            connected = True
        except OperationalError as e:
            connected = False
        if not connected:
            message = self.style.ERROR(
                f'Could not connect to cache.\n{e}'
            )
        else:
            message = self.style.SUCCESS(
                'Connected to cache successfully!'
            )
        self.stdout.write(message)