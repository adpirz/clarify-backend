from django.core.management.base import BaseCommand
from tqdm import tqdm

from experiment.models import StudentWeekCategoryScore


class Command(BaseCommand):
    help = "Update grades with previous and next scores."

    def handle(self, *args, **options):
        all_scores = (StudentWeekCategoryScore.objects
                      .order_by('student_id', 'category_id', 'start_date')
                      .all()
                      )

        for i, score in enumerate(tqdm(all_scores, desc="Scores")):
            previous = None
            previous_3 = None

            if i > 0:
                previous = all_scores[i-1]
            if i > 2:
                previous_3 = all_scores[i-3]

            if previous and previous.category_id == score.category_id:
                previous.next_score = score
                score.previous_score = previous
                score.d_previous = score.primary_metric - previous.primary_metric
                previous.save()

            if previous_3 and previous_3.category_id == score.category_id:
                score.d_three_previous = score.primary_metric - previous_3.primary_metric

            if (previous and previous.category_id == score.category_id) or\
                    (previous_3 and previous_3.category_id == score.category_id):
                score.save()
