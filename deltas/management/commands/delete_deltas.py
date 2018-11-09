from django.core.management.base import BaseCommand

from deltas.models import Delta


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('types', nargs='*', dest='types')

    def handle(self, *args, **options):

        delta_types = [ d[0] for d in Delta.DELTA_TYPE_CHOICES]
        selected_types = options["types"]

        if len(selected_types) > 0:
            for i in selected_types:
                if i not in delta_types:
                    raise ValueError(f'Type {i} is invalid, ' + \
                                     f'must be one of {delta_types}')
        if len(selected_types) == 0:
            Delta.objects.all().delete()
        else:
            Delta.objects.filter(type__in=selected_types).all().delete()

        selected_string = "" if len(selected_types) == 0\
            else f"{''.join(selected_types)} "

        self.stdout.write(
            self.style.SUCCESS(f"Deleted all {selected_string}deltas.")
        )
