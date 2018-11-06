from django.core.management.base import BaseCommand
from tqdm import tqdm

from deltas.models import Delta


class Command(BaseCommand):
    help = "Update old category deltas with gradebook_ids."

    def handle(self, *args, **options):
        deltas = (
            Delta.objects
                .filter(type='category', gradebook_id__isnull=True)
                .prefetch_related('context_record__category')
                .all()
        )

        for delta in tqdm(deltas, desc='Deltas'):
            gradebook_id = delta.context_record.category.gradebook_id
            delta.gradebook_id = gradebook_id
            delta.save()

        success_string = f'Completed update on {len(deltas)} delta' + \
                         f'{"" if len(deltas) == 1 else "s"}'

        self.stdout.write(self.style.SUCCESS(success_string))
