from django.core.management.base import BaseCommand
from django.utils import timezone

from clarify.sync import IlluminateSync
from ._get_models_to_run import get_models_to_run


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('staff_ids', nargs='*'),
        
        parser.add_argument('--disable-logging',
                            action='store_true',
                            dest='log_disable',
                            default=False)

        parser.add_argument('--sparse',
                            action='store_true',
                            dest='sparse',
                            default=False)

        parser.add_argument('--models',
                            dest="models",
                            nargs="+")

    def handle(self, *args, **options):
        selected_ids = options["staff_ids"]
        sparse = options["sparse"]

        sync = IlluminateSync(enable_logging=not options['log_disable'])

        start = timezone.now()
        result_dict = sync.create_all_for_current_staff(
            staff_id_list=selected_ids if selected_ids else None,
            sparse=sparse, models=get_models_to_run(options)
        )
        end = timezone.now()

        minutes, seconds = map(lambda x: round(x), 
                               divmod((end-start).total_seconds(), 60))
                    
        complete_string = "Completed.\n" 
        
        total_new = 0
        total_errors = 0
        
        for model_name, outcome_list in result_dict.items():
            complete_string += f"\t{model_name}: " + \
                               f"{outcome_list[0]} new instances, " + \
                               f"{outcome_list[1]} errors\n"
            
            total_new += outcome_list[0]
            total_errors += outcome_list[1]
        
        complete_string += f"\nTotal new objects: {total_new} | " + \
                           f"Total errors {total_errors} | " + \
                           f"Time elapsed: " + \
                           f"{str(minutes) + ' ' if minutes else ''}" + \
                           f"{'min ' if minutes else ''}{seconds} sec"

        self.stdout.write(self.style.SUCCESS(complete_string))
