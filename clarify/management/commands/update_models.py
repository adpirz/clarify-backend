from django.core.management.base import BaseCommand
from tqdm import tqdm

from clarify.models import Assignment, UserProfile, Gradebook
from clarify.sync import IlluminateSync
from sis_mirror.models import Assignments


class Command(BaseCommand):
    help = "Update selected models from the database."

    def handle(self, *args, **options):

        # for assignment in tqdm(Assignment.objects.all(), desc="Assignments"):
        #     cache_assignment = Assignments.objects.get(
        #         assignment_id=assignment.sis_id)
        #     assignment.is_active = cache_assignment.is_active
        #     assignment.save()
        new_owners = 0

        for profile in tqdm(UserProfile.objects.all(), "Users"):
            staff_id = profile.sis_id
            gradebook_ids = IlluminateSync\
                .get_source_related_gradebooks_for_staff_id(staff_id)

            for gradebook in tqdm(gradebook_ids,
                                  desc="Gradebooks",
                                  leave=False):
                clarify_gradebook = Gradebook.objects.get(
                    sis_id=gradebook["sis_id"])
                if profile not in clarify_gradebook.owners.all():
                    clarify_gradebook.owners.add(profile)
                    new_owners += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done, new m2ms for Gradebook-UserProfile: {new_owners}"))

