import uuid

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from tqdm import tqdm

from sis_mirror.models import Users


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument(
            '--new-passwords',
            dest='passwords',
            action='store_true',
            help='Create new passwords before updating.'
        )

    def handle(self, *args, **options):
        inactive_sis_users = (Users.objects
                          .filter(active=False)
                          .values_list("username", flat=True))

        # Need to turn inactive_sis_users into a list explicitly
        # or else this fails for some reason
        inactive_clarify_users = (User
                          .objects
                          .filter(username__in=list(inactive_sis_users)))

        count = inactive_clarify_users.count()

        success_string = f"Successfully deleted {count} " \
                         f"account{'' if count == 1 else 's'}."

        try:
            dirty_inactive_users = inactive_clarify_users.filter(active=True)
            for user in tqdm(dirty_inactive_users, desc="Inactivating"):
                user.is_active = False
                user.save()
            self.stdout.write(self.style.SUCCESS(success_string))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))

        if options["passwords"]:
            try:
                for u in User.objects.all():
                    u.password = make_password(uuid.uuid4().hex[:10])
                    u.save()
                self.stdout.write(self.style.SUCCESS("Changed all passwords."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
