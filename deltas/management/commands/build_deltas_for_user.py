from django.core.management.base import BaseCommand
from tqdm import tqdm

from sis_mirror.models import Users

from deltas.tasks import (
    build_deltas_for_staff_current_gradebooks,
    build_missing_assignment_deltas_for_user
)


class Command(BaseCommand):
    help = "Build all deltas."

    def add_arguments(self, parser):
        parser.add_argument('users', nargs='+')

    def handle(self, *args, **options):
        staff_ids = self.clean_users(options["users"])

        total_cat = 0
        total_mis = 0

        for staff_id in tqdm(staff_ids, desc="Users"):
            new_cat = build_deltas_for_staff_current_gradebooks(staff_id)
            new_mis, new_mis_err = build_missing_assignment_deltas_for_user(
                staff_id)

            total_cat += new_cat
            total_mis += new_mis

        n = len(staff_ids)

        self.stdout.write(self.style.SUCCESS(
            f'Done for {n} user{"" if n == 1 else "s"}.' +
            f'\n\tNew Category: {total_cat} | New Missing {total_mis}'))

    @classmethod
    def clean_users(cls, users):
        return list(map(cls.clean_user, users))

    @classmethod
    def clean_user(cls, user):
        try:
            user_id = int(user)
        except ValueError:
            user_id = None

        if isinstance(user_id, int):
            try:
                Users.objects.get(pk=user_id)
                return user_id
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