from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from clarify.models import (
    UserProfile, Student, Site, Term, Section,
    SectionGradeLevels, EnrollmentRecord,
    StaffSectionRecord, DailyAttendanceNode,
    Gradebook, Category, Assignment, Score
)

models = [
    User, UserProfile, Student, Site, Term, Section,
    SectionGradeLevels, EnrollmentRecord,
    StaffSectionRecord, DailyAttendanceNode,
    Gradebook, Category, Assignment, Score
]


class Command(BaseCommand):
    help = "Delete all clarify app models."

    def handle(self, *args, **options):
        for model in models:
            d = model.objects.all().delete()
            if d[0] > 0:
                print(model.objects.all().delete())
        self.stdout.write(self.style.SUCCESS('Completed deletion.'))