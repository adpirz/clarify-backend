from django.core.management.base import BaseCommand
from tqdm import tqdm

from clarify.sync import IlluminateSync


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
    
    def handle(self, *args, **options):
        selected_ids = options["staff_ids"]
        sparse = options["sparse"]

        sync = IlluminateSync(enable_logging=not options['log_disable'])
        
        result_dict = sync.create_all_for_current_staff(
            staff_id_list=selected_ids if selected_ids else None,
            sparse=sparse
        )
                    
        complete_string = "Completed.\n" 
        
        total_new = 0
        total_errors = 0
        
        for model_name, outcome_list in result_dict.items():
            complete_string += f"\t{model_name}: " + \
                               f"{outcome_list[0]} new instances, " + \
                               f"{outcome_list[1]} errors\n"
            
            total_new += outcome_list[0]
            total_errors += outcome_list[1]
        
        complete_string += f"Total new objects: {total_new} | " + \
                           f"Total errors {total_errors}"

        self.stdout.write(self.style.SUCCESS(complete_string))
