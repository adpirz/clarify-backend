import json
import datetime

from django.core.management.base import BaseCommand

from sis_pull.models import CategoryScoreCache, Category, Gradebook


def main():
    gradebook_ids = (CategoryScoreCache.objects
                         .exclude(possible_points__isnull=True)
                         .distinct('gradebook_id')
                         .all().values_list('gradebook_id', flat=True)[:100])
    # Blob will have gradebook ids, category ids, category names as an array
    blob = {}
    for gb_id in gradebook_ids:
        gb = Gradebook.objects.get(id=gb_id)
        blob[gb_id] = gb_blob = {'gradebook_name': gb.gradebook_name}
        gb_blob["category_list"] = list(
            gb.category_set.all().values_list('id', 'category_name'))

    now_string = datetime.datetime.now().strftime('%Y-%m-%d--%h-%m')

    with open(f'_testing/Category Grades - {now_string}.json', 'w') as outfile:
        json.dump(blob, outfile)


class Command(BaseCommand):
    help = "Helper for category testing."

    def handle(self, *args, **options):
        main()
        self.stdout.write(self.style.SUCCESS('Successfully completed'))
