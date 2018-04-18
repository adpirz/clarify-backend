from datetime import datetime

from django.db.models import DateTimeField, DateField
from django.utils.timezone import get_current_timezone
from tqdm import tqdm

from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User

from sis_pull.models import (
    Student,
    Staff,
    Site,
    Section,
    Category,
    Course,
    Gradebook,
    AttendanceDailyRecord,
    GradeLevel,
    GradebookSectionCourseAffinity,
    SectionLevelRosterPerYear,
    OverallScoreCache as OSC,
    CategoryScoreCache as CSC,
    AttendanceFlag)

from sis_mirror.models import (
    Students,
    Users,
    Sites,
    AttendanceFlags,
    Sections,
    Categories,
    Courses,
    Gradebooks,
    DailyRecords,
    GradeLevels,
    GradebookSectionCourseAff,
    OverallScoreCache,
    SsCube,
    CategoryScoreCache
)


def fields_list(model, remove_autos=True, keep_fks=True, return_fks=False):
    """
    Return list of model field instances (subclass django.db.model.fields)
    :param model: Django model instance or base class
    :param remove_autos: Remove auto_created fields
    :param keep_fks: Keep foreign_key fields
    :param return_fks: Return only foreign_key fields (trumps other settings)
    :return: Django Model Field instance
    """
    fields = model._meta.get_fields()

    if return_fks:
        return [f for f in fields if isinstance(f, ForeignKey)]
    if not keep_fks:
        fields = filter(lambda f: not f.related_model, fields)
    if remove_autos:
        fields = filter(lambda f: not f.auto_created, fields)

    return fields


def field_in_list(field, field_list):
    """
    Returns if field in field_list
    :param field: Django Model Field instance
    :param field_list: List[Field]
    :return: Boolean
    """
    alt = field.name + '_id'

    names = field_list_to_names(field_list)

    return field.name in names or alt in names


def field_list_to_names(field_list):
    """
    Turns list of field instances to field names
    :param field_list: List[Field]
    :return: List[str]: field.name
    """
    return [i.name for i in field_list]


def sis_to_django_model(sis_model, django_model, source_id_field=None,
                        field_map=None):
    """
    Pull SIS models into Django models

    :param sis_model: Base SIS Model Class
    :param django_model: Base Django Model Class
    :param source_id_field: SIS column for id
    :param field_map: [Optional] Django field: SIS field mapping
    :return: None
    """
    django_fields = field_list_to_names(fields_list(django_model))
    sis_fields = field_list_to_names(fields_list(sis_model,
                                                remove_autos=False))

    django_model_name = django_model.__name__

    # Get all Django model fields in SIS model,
    # including '_id' suffixed fields for FK's
    out_fields = list()
    for field in django_fields:
        alt = field + '_id'
        if field in sis_fields:
            out_fields.append(field)
        elif alt in sis_fields:
            out_fields.append(alt)
        else:
            pass

    # All SIS model instances
    sis_rows = sis_model.objects.all()
    new_models = 0
    errors = 0

    # Progress bar for each row in SIS table
    for row in tqdm(sis_rows, desc=django_model_name):
        # For each row in SIS table, put the value
        # of each overlapping field in a dict
        model_args = dict()
        for field in out_fields:
            model_args[field] = row.__getattribute__(field)

        # Convenience method if you need to map Django model field
        # to SIS model field
        if field_map:
            for dj_field, sis_field in field_map.items():
                model_args[dj_field] = row.__getattribute__(sis_field)

        # For SIS tables with primary key (ie, non-view tables),
        # use the source_id_field to get source_object_id
        if source_id_field:
            model_args['source_object_id'] = row.\
                __getattribute__(source_id_field)

        # Get FK fields that are not user (special case that has
        # to be handled differently because of Staff <> User rel)
        fk_fields = fields_list(django_model, return_fks=True)
        fk_fields = filter(lambda i: i is not 'user', fk_fields)

        for field in fk_fields:
            # For each FK field, get the foreign object by SIS id,
            # then get it's Django id to pass into model_args
            get_name = field.name if field.name.split('_')[-1] == 'id'\
                else field.name + '_id'
            fk_pk = field.related_model.objects.get(
                source_object_id=row.__getattribute__(get_name)).pk
            model_args = {k: v for k, v in model_args.items() if k is not field.name}
            model_args[field.name + '_id'] = fk_pk

        # Datetime cleanup with timezones
        for field in fields_list(django_model):
            if field.name in model_args and isinstance(field, DateTimeField):
                tz = get_current_timezone()
                old_date = model_args[field.name]
                model_args[field.name] = tz.localize(old_date)

        model, created = django_model.objects.get_or_create(**model_args)
        if created:
            new_models += 1

    print("NEW {} MODELS CREATED: {}".format(django_model_name, new_models))
    print(f"ERRORS: {errors}")


def build_staff_from_sis_users():
    users = Users.objects.all()
    user_fields = ['username', 'first_name', 'last_name']

    users_created = 0
    staff_created = 0

    dj_user_models = []
    for user in tqdm(users, desc="Users"):
        model_args = {field: user.__getattribute__(field)
                      for field in user_fields}
        model, created = User.objects.get_or_create(**model_args)
        if created:
            users_created += 1
        dj_user_models.append(model)

    for dj_user in tqdm(dj_user_models, desc="Staff"):
        sis_user = Users.objects.get(username=dj_user.username)
        dj_field_list = field_list_to_names(fields_list(Staff))
        excluded_fields = ['user', 'prefix', 'source_object_id']
        dj_field_list = filter(
            lambda i: i not in user_fields and i not in excluded_fields,
            dj_field_list)

        model_args = dict()
        for field in dj_field_list:
            model_args[field] = sis_user.__getattribute__(field)

        if sis_user.gender == 'M':
            model_args['prefix'] = 'MR'
        else:
            model_args['prefix'] = 'MS'

        model, created = Staff.objects.\
            get_or_create(
                source_object_id=sis_user.user_id, user_id=dj_user.id,
                **model_args)

        if created:
            staff_created += 1

    print("NEW USERS CREATED: ", users_created)
    print("NEW STAFF CREATED: ", staff_created)


def main():
    build_staff_from_sis_users()
    args_list = [
        (AttendanceFlags, AttendanceFlag, 'attendance_flag_id'),
        (Students, Student, 'student_id'),
        (GradeLevels, GradeLevel, 'grade_level_id'),
        (Sites, Site, 'site_id'),
        (Courses, Course, 'course_id'),
        (Sections, Section, 'section_id'),
        (SsCube, SectionLevelRosterPerYear),
        (Gradebooks, Gradebook, 'gradebook_id'),
        (OverallScoreCache, OSC),
    ]

    for args in args_list:
        sis_to_django_model(*args)
    sis_to_django_model(DailyRecords, AttendanceDailyRecord)


def delete_all():
    models = [
        AttendanceFlag, Student, GradeLevel, Site, Course,
        Section, SectionLevelRosterPerYear, Gradebook,
        OverallScoreCache
    ]

    for model in tqdm(models, desc="Deleting all models"):
        model.objects.all().delete()
