from django.core.management.base import BaseCommand
from tqdm import tqdm

from clarify.models import Assignment
from sis_mirror.models import Assignments


class Command(BaseCommand):
    help = "Update selected models from the database."

    def handle(self, *args, **options):
        for assignment in tqdm(Assignment.objects.all(), desc="Assignments"):
            cache_assignment = Assignments.objects.get(
                assignment_id=assignment.sis_id)
            assignment.is_active = cache_assignment.is_active
            assignment.save()



