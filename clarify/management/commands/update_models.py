from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tqdm import tqdm

from clarify.models import Assignment, UserProfile, Gradebook, Score
from clarify.sync import IlluminateSync
from deltas.models import Delta
from sis_mirror.models import Assignments, ScoreCache


class Command(BaseCommand):
    help = "Update selected models from the database."

    def handle(self, *args, **options):

        deltas = (Delta.objects
                  .filter(type="category",
                          category_average_before__exact=0)
                  .all()
                  )

        for d in tqdm(deltas, desc="First score deltas"):
            d.delete()

        scores = (Score
                  .objects
                  .filter(percentage__isnull=True)
                  .all())

        for score in tqdm(scores, desc="Score percentages"):
            cache_score = ScoreCache.objects.get(cache_id=score.sis_id)
            score.percentage = cache_score.percentage
            score.save()

        assignments = (Assignment
                       .objects
                       .filter(due_date__isnull=True)
                       .all())

        for assignment in tqdm(assignments, desc="Assignments"):
            cache_assignment = Assignments.objects.get(
                assignment_id=assignment.sis_id)
            assignment.due_date = cache_assignment.due_date
            assignment.save()

        new_owners = 0

        for profile in tqdm(UserProfile.objects.all(), "User gradebooks"):
            staff_id = profile.sis_id
            gradebook_ids = IlluminateSync\
                .get_source_related_gradebooks_for_staff_id(staff_id)

            for gradebook in gradebook_ids:
                clarify_gradebook = Gradebook.objects.get(
                    sis_id=gradebook["sis_id"])
                if profile not in clarify_gradebook.owners.all():
                    clarify_gradebook.owners.add(profile)
                    new_owners += 1

        new_email_saves = 0

        for user in tqdm(User.objects.filter(email__isnull=True).all(),
                          desc="User email updating"):
            if not user.email:
                user.email = user.username
                user.save()
                new_email_saves += 1