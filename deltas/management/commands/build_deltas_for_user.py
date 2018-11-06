from django.core.management.base import BaseCommand
from tqdm import tqdm

from sis_mirror.models import Users

from deltas.tasks import build_deltas_for_all_current_academic_teachers


class Command(BaseCommand):
    help = "Build all deltas."

    def handle(self, *args, **options):
        build_deltas_for_all_current_academic_teachers()

    @classmethod
    def clean_users(cls, users):
        return map(cls.clean_user, users)

    @classmethod
    def clean_user(cls, user):
        try:
            user_id = int(user)
        except ValueError:
            user_id = None

        if isinstance(user_id, int):
            try:
                Users.objects.get(pk=user_id)
                return user
            except Users.DoesNotExist as e:
                return cls.clean_user(input(
                    "User ID doesn't exist, please enter another user: "
                    )
                )
        try:
            u = Users.objects.get(username__istartswith=user)
            response = input(
                f'Did you want user {u.username} ({u.user_id})? [Y/n] '
            )

            while response.lower() not in ['', 'y', 'yes', 'n', 'no']:
                response = input('Please respond yes or no.')

            if response.lower() in ['y', 'yes', '']:
                return u.user_id
            else:
                return cls.clean_user(input("Please enter another user: "))

        except Users.MultipleObjectsReturned:
            return cls.clean_user(input(
                "Too many objects returned, please input another user: "
                )
            )