from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from pprint import pformat
from django.conf import settings


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        db_conn = connections['cache']
        try:
            c = db_conn.cursor()
            connected = True
        except OperationalError:
            connected = False
        if not connected:
            message = self.style.ERROR(
                f'Could not connect to cache.\n'
                f'settings.DATABASES["cache"]:\n' +
                pformat(settings.DATABASES["cache"])
            )
        else:
            message = self.style.SUCCESS(
                'Connected to cache successfully!'
            )
        self.stdout.write(message)