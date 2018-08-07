from django.core.management.base import BaseCommand

from sis_mirror.models import Sites
from sis_pull.models import Site


class Command(BaseCommand):
    help = "Add 'has_students' to existing sites."

    def handle(self, *args, **options):
        for s in Site.objects.all():
            sis_site = Sites.objects.get(pk=s.pk)
            s.has_students = sis_site.has_students
            s.save()

        self.stdout.write(self.style.SUCCESS('Completed'))

