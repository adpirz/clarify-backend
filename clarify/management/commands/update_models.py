from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from clarify.models import Assignment, UserProfile, Gradebook
from clarify.sync import IlluminateSync
from sis_mirror.models import Assignments


class Command(BaseCommand):
    help = "Update selected models from the database."

    def handle(self, *args, **options):

        assignments = (Assignment
                       .objects
                       .filter(is_active__isnull=True)
                       .all())

        for assignment in tqdm(assignments, desc="Assignments"):
            cache_assignment = Assignments.objects.get(
                assignment_id=assignment.sis_id)
            assignment.is_active = cache_assignment.is_active
            assignment.save()

        new_owners = 0

        for profile in tqdm(UserProfile.objects.all(), "Users"):
            staff_id = profile.sis_id
            gradebook_ids = IlluminateSync\
                .get_source_related_gradebooks_for_staff_id(staff_id)

            for gradebook in gradebook_ids:
                clarify_gradebook = Gradebook.objects.get(
                    sis_id=gradebook["sis_id"])
                if profile not in clarify_gradebook.owners.all():
                    clarify_gradebook.owners.add(profile)
                    new_owners += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done, new m2ms for Gradebook-UserProfile: {new_owners}"))

        new_email_saves = 0

        for user in tqdm(User.objects.all(),
                          desc="User email updating"):
            if not user.email:
                user.email = user.username
                user.save()
                new_email_saves += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done, new emails saved: {new_email_saves}"))