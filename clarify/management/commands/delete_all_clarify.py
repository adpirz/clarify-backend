from django.core.management.base import BaseCommand

from ._get_models_to_run import get_models_to_run


class Command(BaseCommand):
    help = "Delete all clarify app models."

    def add_arguments(self, parser):
        parser.add_argument('--models',
                            nargs='+',
                            dest='models')

    def handle(self, *args, **options):
        models_to_run = get_models_to_run(options, none_if_empty=False)

        for model in models_to_run:
            model.objects.all().delete()

        model_names = [m.__name__ for m in models_to_run]
        out_string = "Completed deletion.\n" \
                     f"Models run: {', '.join(model_names)}\n"

        self.stdout.write(self.style.SUCCESS(out_string))