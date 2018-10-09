import pytz
import uuid
from collections import OrderedDict

from django.db import IntegrityError
from django.db.models import DateTimeField, DateField
from django.utils import timezone
from tqdm import tqdm

from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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
    AttendanceFlag,
    SectionTimeblockAffinity,
    Timeblock,
    CurrentRoster,
    Assignment,
    ScoreCache as SC,
    Scores as Pull_scores,
    SessionType,
    Session,
    Role,
    Term,
    StaffTermRoleAffinity
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
    CategoryScoreCache,
    SectionTimeblockAff,
    Timeblocks,
    SsCurrent,
    Assignments,
    ScoreCache,
    Scores,
    SessionTypes,
    Sessions,
    Roles,
    Terms,
    UserTermRoleAff
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


def field_list_to_names(field_list):
    """
    Turns list of field instances to field names
    :param field_list: List[Field]
    :return: List[str]: field.name
    """
    return [i.attname if hasattr(i, 'attname') else i.name
            for i in field_list]


def sis_to_django_model(sis_model, clarify_model,
                        field_map=None, no_bulk=False):
    """
    Pull SIS models into Django models

    :param sis_model: Base SIS Model Class
    :param clarify_model: Base Django Model Class
    :param field_map: Dict; map of sis_field to clarify_model field
    :param no_bulk: Boolean; force any views or bulk inserts to do row by row
    :return: None
    """
    clarify_model_fields = field_list_to_names(fields_list(clarify_model))
    sis_fields = field_list_to_names(fields_list(sis_model,
                                                 remove_autos=False))

    source_id_field = clarify_model.source_id_field

    clarify_model_name = clarify_model.__name__

    out_fields = [i for i in clarify_model_fields if i in sis_fields]

    # bulk create views
    bulk = True if not no_bulk else False

    # All SIS model instances
    if not hasattr(sis_model, 'pull_query'):
        sis_rows = sis_model.objects.all()
    else:
        sis_rows = sis_model.pull_query()

    new_models = 0
    model_errors = 0

    if bulk:
        bulk_list = []

    # tqdm: Progress bar for each row in SIS table
    # set monitor_interval = 0 to prevent a thread
    # exception on large bulk inserts
    # see: https://github.com/tqdm/tqdm/issues/469

    tqdm.monitor_interval = 0

    for row in tqdm(sis_rows, desc=clarify_model_name):
        # For each row in SIS table, put the value
        # of each overlapping field in a dict
        model_args = dict()
        for field_name in out_fields:
            model_args[field_name] = row.__getattribute__(field_name)

        # For field in mapped fields:
        if field_map:
            for sis_field, clarify_field in field_map.items():
                model_args[clarify_field] = row.__getattribute__(sis_field)

        # For SIS tables with primary key (ie, non-view tables),
        # use the source_id_field to get source_object_id
        if source_id_field:
            model_args['id'] = row.\
                __getattribute__(source_id_field)
        # Datetime cleanup with timezones
        for field in fields_list(clarify_model):
            if field.name in model_args and isinstance(field, DateTimeField):
                old_date_time = model_args[field.name]
                model_args[field.name] = pytz.utc.localize(old_date_time) \
                    if old_date_time else None

        if bulk:
            bulk_list.append(clarify_model(**model_args))
            new_models += 1
        else:
            try:
                model, created = clarify_model.objects.get_or_create(**model_args)
                if created:
                    new_models += 1
            except IntegrityError as e:
                model_errors += 1

    if bulk:
        print("\tBulk creating {}...".format(clarify_model_name))
        clarify_model.objects.bulk_create(bulk_list, batch_size=100000)
        print("\tBulk create complete!\n".format(clarify_model_name))

    print(f"\tNew {clarify_model_name} instances created: {new_models}" + \
          f"\n\tErrors: {model_errors}.")


def build_staff_from_sis_users():
    users = Users.objects.all()
    user_fields = ['username', 'first_name', 'last_name']

    # KEY - sis_mirror field, VALUE - sis_pull field
    user_mapped_fields = { "active": "is_active" }

    users_created = 0
    staff_created = 0

    dj_user_models = []

    for user in tqdm(users, desc="Users"):
        # Create auth.models.User objects
        # from SIS Users
        model_args = {field: user.__getattribute__(field)
                      for field in user_fields}

        for mirror_field, pull_field in user_mapped_fields.items():
            model_args[pull_field] = user.__getattribute__(mirror_field)

        # create a password
        model_args["password"] = make_password(uuid.uuid4().hex[:10])
        model, created = User.objects.get_or_create(**model_args)

        if created:
            users_created += 1

        dj_user_models.append(model)

    for dj_user in tqdm(dj_user_models, desc="Staff"):
        # Take User objects and create associated
        # Staff objects
        sis_user = Users.objects.get(username=dj_user.username)
        dj_field_list = field_list_to_names(fields_list(Staff))

        # Leave out fields not in user model, also leave out
        # user so we can pull the proper Django user later
        excluded_fields = ['user', 'prefix']
        dj_field_list = filter(
            lambda i: i not in user_fields and i not in excluded_fields,
            dj_field_list)

        model_args = dict()
        for field in dj_field_list:
            if field != "user_id":
                model_args[field] = sis_user.__getattribute__(field)

        if sis_user.gender == 'M':
            model_args['prefix'] = 'MR'
        else:
            model_args['prefix'] = 'MS'

        model, created = Staff.objects. \
            get_or_create(
                id=sis_user.user_id, user_id=dj_user.id,
                **model_args)

        if created:
            staff_created += 1

    print(f"\tNew User models created: {users_created}; " +
          f"New Staff models created: {staff_created}\n")


def main(**options):
    clean = options['clean']
    no_bulk = options['no_bulk']
    selected_models = options['models']

    models_to_run = []

    # We make an ordered dict so that getting the
    # keys gives us a proper insertion order for
    # FK dependencies
    user_staff_map = {'user_id': 'staff_id'}

    model_dict = OrderedDict({
        'attendance_flags': (AttendanceFlags, AttendanceFlag),
        'students': (Students, Student),
        'users': True,
        'grade_levels': (GradeLevels, GradeLevel),
        'sites': (Sites, Site),
        'ss_current': (SsCurrent, CurrentRoster),
        'courses': (Courses, Course),
        'sections': (Sections, Section),
        'ss_cube': (SsCube, SectionLevelRosterPerYear, user_staff_map),
        'gradebooks': (Gradebooks, Gradebook),
        'timeblocks': (Timeblocks, Timeblock),
        'stba': (SectionTimeblockAff, SectionTimeblockAffinity),
        'gsca': (GradebookSectionCourseAff,
                 GradebookSectionCourseAffinity, user_staff_map),
        'overallscorecache': (OverallScoreCache, OSC),
        'daily_records': (DailyRecords, AttendanceDailyRecord),
        'categories': (Categories, Category),
        'csc': (CategoryScoreCache, CSC,),
        'assignments': (Assignments, Assignment,),
        'scorecache': (ScoreCache, SC),
        'sessiontypes': (SessionTypes, SessionType),
        'sessions': (Sessions, Session),
        'roles': (Roles, Role),
        'terms': (Terms, Term),
        'usta': (UserTermRoleAff, StaffTermRoleAffinity, user_staff_map),
        'scores': (Scores, Pull_scores),
    })

    model_dict_keys = model_dict.keys()

    if len(selected_models) == 0:
        models_to_run += model_dict_keys
    else:
        models_to_run += filter(
            lambda m: m in selected_models,
            model_dict_keys
        )

    if len(models_to_run) == 0:
        raise ValueError('Invalid model choices. Options are: {}'.format(
            ', '.join(model_dict_keys)
        ))

    for model in models_to_run:
        args = model_dict[model]
        kwargs = {}

        django_model = Staff if model == "users" else args[1]

        if no_bulk:
            kwargs['no_bulk'] = True

        if clean:
            django_model.objects.all().delete()
            delete_string = django_model.__name__

            if django_model == Staff:
                User.objects.all().delete()
                delete_string += ', User'

            print("Deleted all instances of {}".format(delete_string))

        if model == "users":
            build_staff_from_sis_users()
        else:
            sis_to_django_model(*args, **kwargs)

    return models_to_run


def clean_all():
    models = [
        AttendanceFlag, Student, GradeLevel, Site, Course,
        Section, SectionLevelRosterPerYear, Gradebook,
        OSC
    ]

    for model in tqdm(models, desc="Deleting all models"):
        model.objects.all().delete()
