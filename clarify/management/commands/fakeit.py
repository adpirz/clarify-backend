from django.core.management.base import BaseCommand
from tqdm import tqdm
from mimesis import Person

from clarify.models import Student, UserProfile
from sis_mirror.models import Students, Users


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--unfake',
                            dest="unfake",
                            action="store_true")

    def handle(self, *args, **options):
        unfake = options["unfake"]
        if unfake:
            self.unfake()
        else:
            self.fake()

    def fake(self):
        p = Person()
        students = Student.objects.filter(sis_id__isnull=False).all()
        for student in tqdm(students,
                            desc="Faking students",
                            leave=False):
            student.first_name = p.name()
            student.last_name = p.last_name()
            student.save()

        profiles = UserProfile.objects.filter(sis_id__isnull=False).all()
        for profile in tqdm(profiles,
                            desc="Faking users",
                            leave=False):
            user = profile.user
            user.first_name = p.name()
            user.last_name = p.last_name()
            user.save()

        self.stdout.write(self.style.SUCCESS(
            f'Faked {len(students)} students and {len(profiles)} users.'))

    def unfake(self):
        students = Student.objects.filter(sis_id__isnull=False).all()
        for student in tqdm(students,
                            desc="Unfaking students",
                            leave=False):
            real_student = Students.objects.get(student_id=student.sis_id)
            student.first_name = real_student.first_name
            student.last_name = real_student.last_name
            student.save()

        profiles = UserProfile.objects.filter(sis_id__isnull=False).all()
        for profile in tqdm(profiles,
                            desc="Unaking users",
                            leave=False):
            real_user = Users.objects.get(user_id=profile.sis_id)
            user = profile.user
            user.first_name = real_user.first_name
            user.last_name = real_user.last_name
            user.save()

        self.stdout.write(self.style.SUCCESS(
            f'Unfaked {len(students)} students and {len(profiles)} users.'))

