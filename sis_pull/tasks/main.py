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
    CategoryScoreCache as CSC
)

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

pairs = [(Student, Students), (Staff, Users), (Site, Sites),
         (Section, Sections), (Category, Categories),
         (Course, Courses), (Gradebook, Gradebooks),
         (AttendanceDailyRecord, DailyRecords), (GradeLevel, GradeLevels),
         (GradebookSectionCourseAffinity, GradebookSectionCourseAff),
         (OSC, OverallScoreCache), (CSC, CategoryScoreCache)]


def fields_list(model, remove_autos=True, keep_fks=True, return_fks=False):
    fields = model._meta.get_fields()

    if return_fks:
        return [f for f in fields if isinstance(f, ForeignKey)]
    if not keep_fks:
        fields = filter(lambda f: not f.related_model, fields)
    if remove_autos:
        fields = filter(lambda f: not f.auto_created, fields)

    return fields


def field_in_list(field, field_list):
    alt = field.name + '_id'

    names = field_list_to_names(field_list)

    return field.name in names or alt in names


def field_list_to_names(field_list):
    return [i.name for i in field_list]


def pair_diffs(pair):
    model1, model2 = [i.__name__ for i in pair]
    field1 = fields_list(pair[0])
    field2 = fields_list(pair[1], remove_autos=False)

    notin2 = [i for i in field1 if not field_in_list(i, field2)]

    if len(notin2) > 0:
        print('{} fields not in {}: '.format(model1, model2),
              field_list_to_names(notin2))


def pair_same(pair):
    model1, model2 = [i.__name__ for i in pair]
    field1 = fields_list(pair[0])
    field2 = fields_list(pair[1], remove_autos=False)


SOURCE_OBJECT_MAPS = {
    'students': 'student_id'
}
MAPS = {
    # Django field : SIS field
    # first children are the django models
    "Student": {
        "ethnicity": "primary_ethnicity"
    },
}


def sis_to_django_model(sis_model, django_model, source_id_field=None,
                        field_map=None):
    """

    :param sis_model: Base SIS Model Class
    :param django_model: Base Django Model Class
    :param source_id_field: SIS column for id
    :param field_map: [Optional] Django field: SIS field mapping
    :return:
    """
    django_fields = field_list_to_names(fields_list(django_model))
    sis_fields = field_list_to_names(fields_list(sis_model,
                                                remove_autos=False))

    django_model_name = django_model.__name__
    sis_model_name = sis_model.__name__

    # Get all overlapping fields
    out_fields = list()
    for field in django_fields:
        alt = field + '_id'
        if field in sis_fields:
            out_fields.append(field)
        elif alt in sis_fields:
            out_fields.append(alt)
        else:
            pass

    # all sis models
    sis_rows = sis_model.objects.all()
    new_models = 0
    errors = 0
    for row in tqdm(sis_rows, desc=django_model_name):
        model_args = dict()
        for field in out_fields:
            model_args[field] = row.__getattribute__(field)

        if field_map:
            for dj_field, sis_field in field_map.items():
                model_args[dj_field] = row.__getattribute__(sis_field)

        if source_id_field:
            model_args['source_object_id'] = row.\
                __getattribute__(source_id_field)

        fk_fields = fields_list(django_model, return_fks=True)
        fk_fields = filter(lambda i: i is not 'user', fk_fields)

        for field in fk_fields:
            get_name = field.name if field.name.split('_')[-1] == 'id'\
                else field.name + '_id'
            fk_pk = field.related_model.objects.get(
                source_object_id=row.__getattribute__(get_name)).pk
            model_args = {k: v for k, v in model_args.items() if k is not field.name}
            model_args[field.name + '_id'] = fk_pk

        # date time clean up
        for field in fields_list(django_model):
            if field.name in model_args and\
                    (isinstance(field, DateTimeField) or\
                     isinstance(field, DateField)):
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
    # build_staff_from_sis_users()
    args_list = [
        # (Students, Student, 'student_id')
        # (GradeLevels, GradeLevel, 'grade_level_id'),
        # # (Sites, Site, 'site_id'),
        # # # (DailyRecords, AttendanceDailyRecord),
        # (Courses, Course, 'course_id'),
        # (Sections, Section, 'section_id'),
        # (SsCube, SectionLevelRosterPerYear),
        (Gradebooks, Gradebook),
        (Categories, Category),
    ]

    for args in args_list:
        sis_to_django_model(*args)
