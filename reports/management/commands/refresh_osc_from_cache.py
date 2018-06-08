from django.core.management.base import BaseCommand, CommandError
from sis_pull.models import OverallScoreCache, Student, Gradebook
from sis_mirror.models import OverallScoreCache as OSC
from tqdm import tqdm
import pytz


class Command(BaseCommand):
    help = 'Rebuilds sis_pull OverallScoreCache from sis_mirror'

    def handle(self, *args, **options):
        caches = []
        for cache in tqdm(OSC.objects.all(), desc="Cache"):
            student_id = Student.objects.\
                get(source_object_id=cache.student_id).id
            gradebook_id = Gradebook.objects.\
                get(source_object_id=cache.gradebook_id).id

            caches.append(OverallScoreCache(
                student_id=student_id,
                gradebook_id=gradebook_id,
                possible_points=cache.possible_points,
                points_earned=cache.points_earned,
                percentage=cache.percentage,
                mark=cache.mark,
                missing_count =cache.missing_count,
                zero_count=cache.zero_count,
                excused_count=cache.excused_count,
                calculated_at=pytz.utc.localize(cache.calculated_at)
            ))

        OverallScoreCache.objects.bulk_create(caches)

        self.stdout.write(self.style.SUCCESS(
            'Built new OverallScoreCache models'
        ))