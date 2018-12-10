from datetime import datetime
from django.core.management.base import BaseCommand
from clarify.models import (UserProfile, Section, Student, EnrollmentRecord,
StaffSectionRecord, Site, Term)
from django.contrib.auth.models import User
from clarify_backend.scripts.manual_roster import manually_roster_with_file


class Command(BaseCommand):
    help = """Manually roster students for a teacher not using Clever or an SIS. Takes a path to a
    file containing tuples of ("student_last_name", "student_first_initial", "class_name'), delimited by new lines."""

    def handle(self, *args, **options):
        kwargs = {}
        kwargs['first_name'] = input('Enter the teacher\'s first name:')
        kwargs['last_name'] = input('Enter the teacher\'s last name:')
        kwargs['teacher_username'] = input('Enter the username for the new teacher:')
        kwargs['password'] = input('Enter a password for the new teacher:')
        kwargs['prefix'] = input('Enter what prefix the teacher would like:')

        kwargs['site_name'] = input('What is the name of the new teacher\'s school:')

        source_filename = input('Enter the path to the file containing the student names:')

        with open(source_filename, 'r') as source_filename:
            manually_roster_with_file(source_filename, **kwargs)





