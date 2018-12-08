from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from clarify.models import (UserProfile, Section, Student, EnrollmentRecord,
StaffSectionRecord, Site, Term)
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = """Manually roster students for a teacher not using Clever or an SIS. Takes a path to a
    file containing tuples of ("student_last_name", "student_first_initial", "class_name'), delimited by new lines."""

    def handle(self, *args, **options):
        student_tuple_list = []

        first_name = input('Enter the teacher\'s first name:')
        last_name = input('Enter the teacher\'s last name:')
        teacher_username = input('Enter the username for the new teacher:')
        password = input('Enter a password for the new teacher:')
        prefix = input('Enter what prefix the teacher would like:')
        new_user = User.objects.create(
                    username=teacher_username,
                    first_name=first_name,
                    last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        new_teacher_user_profile = UserProfile.objects.create(user=new_user, prefix=prefix)

        # site_name = input('What is the name of the new teacher\'s school:')
        new_site = Site.objects.create(name='Saint Paul Central High School')
        new_term = (Term.objects.create(
                    name='All Year',
                    site=new_site,
                    start_date=datetime(2018, 8, 1),
                    end_date=datetime(2019, 6, 1),
                    academic_year=2019))


        default_section_name = f"Mr. Cherin's class"
        section_names = [default_section_name]
        created_sections = []
        student_list = []
        source_filename = "clarify/management/commands/cherin_students.py";

        with open(source_filename, 'r') as open_file:
            # Every line in the file should be of the form first_name last_name class_name, with
            # class_name optional
            for line in open_file:
                student_array = line.strip().split()
                new_student = {
                    'first_name': student_array[0],
                    'last_name': student_array[1],
                }
                try:
                    next_section_name = student_array[2]
                    new_student.section_name = next_section_name
                    if next_section_name not in section_name:
                        section_names.append(next_section_name)
                except IndexError:
                    new_student['section_name'] = default_section_name
                student_list.append(new_student)
            for student in student_list:
                new_student = Student.objects.create(
                                first_name=student.get('first_name'),
                                last_name=student.get('last_name'))
                students_section = [section for section in created_sections if section.name == student.get('section_name')]
                if not len(students_section):
                    new_section = Section.objects.create(
                                    name=student.get('section_name'),
                                    course_name=student.get('section_name'),
                                    term=new_term)
                    created_sections.append(new_section)
                    EnrollmentRecord.objects.create(student=new_student, section=new_section)
                else:
                    EnrollmentRecord.objects.create(student=new_student, section=students_section[0])
            for section in created_sections:
                StaffSectionRecord.objects.create(
                                    user_profile=new_teacher_user_profile,
                                    section=section,
                                    active=True)


