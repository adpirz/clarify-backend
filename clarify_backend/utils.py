import re
from datetime import datetime
from django.utils import timezone

from django.db import models, IntegrityError
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from sendgrid import Email
from sendgrid.helpers.mail import Content, Mail

from clarify.models import (
    UserProfile, Section, Student, EnrollmentRecord,
    StaffSectionRecord, Site, Term
)


def try_bulk_or_skip_errors(model, instance_list):
    new, errors = 0, 0

    try:
        model.objects.bulk_create(instance_list)
        new = len(instance_list)
    except IntegrityError:
        for instance in instance_list:
            try:
                instance.save()
                new += 1
            except IntegrityError:
                errors += 1
                continue

    return new, errors

def camel_to_underscore(name):
    """
    See here: http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case

    >>> camel_to_underscore('CamelCase')
    'camel_case'
    >>> camel_to_underscore('CamelCamelCase')
    'camel_camel_case'
    >>> camel_to_underscore('Camel2Camel2Case')
    'camel2_camel2_case'
    >>> camel_to_underscore('getHTTPResponseCode')
    'get_http_response_code'
    >>> camel_to_underscore('get2HTTPResponseCode')
    'get2_http_response_code'
    >>> camel_to_underscore('HTTPResponseCode')
    'http_response_code'
    >>> camel_to_underscore('HTTPResponseCodeXYZ')
    'http_response_code_xyz'

    """

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_academic_year(date=None):
    return 2019
    # today = date or timezone.now().date()
    # return today.year if today.month < 8 else today.year + 1


def SourceObjectForeignKey(fk_model, **kwargs):
    return models.ForeignKey(fk_model, to_field='source_object_id', **kwargs)


GRADE_TO_GPA_POINTS = {
    "A+": 4.33,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.33,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.2,
    "D": 1.0,
    "D-": 0,
    "F": 0,
    "NCR": 1.0,
    "Not College Ready": 1.0
}

def manually_roster_with_file(source_file, **kwargs):
    new_user = User.objects.create(
                username=kwargs['username'],
                first_name=kwargs['first_name'],
                last_name=kwargs['last_name'])
    new_user.set_password(kwargs['temporary_password'])
    new_user.save()

    new_teacher_user_profile = UserProfile.objects.create(user=new_user, prefix=kwargs['prefix'])
    new_site = Site.objects.create(name=kwargs['school_name'])
    new_term = (Term.objects.create(
                name='All Year',
                site=new_site,
                start_date=datetime(2018, 8, 1),
                end_date=datetime(2019, 6, 1),
                academic_year=2019))

    default_section_name = f"{kwargs['prefix']} {kwargs['last_name']}'s class"
    section_names = [default_section_name]
    created_sections = []
    student_list = []

    with source_file as open_file:
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

def word_hash(length=4):
    species = sample(WORDS["species"], 1)[0].replace(' ', '')
    words = "".join([sample(WORDS["words"], 1)[0].lower().capitalize()
                    for _ in range(length - 1)])

    return species + words


def build_reset_email(request, profile: UserProfile):
    if not profile.reset_token:
        raise AttributeError("No reset token found")
    name = profile.get_full_name()
    reset_token = profile.reset_token
    domain = request.META['HTTP_HOST']
    protocol = 'https' if request.is_secure() else 'http'

    from_email = Email("noreply@clarify.school")
    to_email = Email(profile.user.email)
    subject = f"Reset password for {name}"
    body = "To reset your password, please click the link below.\n\n" \
           f"{protocol}://{domain}/password-reset/?token={reset_token}"

    content = Content("text/plain",
                      body)

    return Mail(from_email, subject, to_email, content)
