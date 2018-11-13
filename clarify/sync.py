from django.contrib.auth.models import User
from django.db.models import Model
from django.utils import timezone
from tqdm import tqdm

from sis_mirror.models import (
    Sites,
    Terms,
    Students,
    Sections,
    SectionStudentAff,
    Gradebooks,
    Categories,
    Assignments,
    ScoreCache,
    Users)

from clarify.models import (
    Student,
    UserProfile,
    Site,
    Term,
    Section,
    EnrollmentRecord,
    StaffSectionRecord,
    DailyAttendanceNode,
    Gradebook, Category, Assignment)


class Sync:
    source_id_field = None

    def __init__(self, logger=None, enable_logging=True):
        self.logger = (logger or print) if enable_logging else None

    def log(self, *args, **kwargs):
        if self.logger:
            return self.logger(*args, **kwargs)

        return None

    @classmethod
    def get_or_create_staff(cls, source_id):
        """
        Create Staff and User if doesn't exist for given source_id
        :param source_id: String; name of source field on Staff
        :param model_kwargs: Dict of user + staff properties
        :return:
        """
        if not (UserProfile.objects
                .filter(**{cls.source_id_field: source_id})
                .exists()):

            model_kwargs = cls.get_source_related_staff_for_staff_id(source_id)
            email = model_kwargs["email"]
            first_name = model_kwargs.get("first_name", "")
            last_name = model_kwargs.get("last_name", "")
            username = model_kwargs.get("username", None) or email
            user = User.objects.create(
                username=username, email=email,
                first_name=first_name, last_name=last_name
            )

            name = model_kwargs.get("name", "")
            prefix = model_kwargs.get("prefix", "")

            # match signature of Model.objects.get_or_create:
            # > Returns a tuple of (object, created)

            return UserProfile.objects.create(
                user=user, name=name, prefix=prefix
            ), 1

        # match signature of Model.objects.get_or_create:
        # > Returns a tuple of (object, created)

        return UserProfile.objects.get(**{
            cls.source_id_field: source_id
        }), 0

    """ All methods below pull only current records """

    @classmethod
    def get_source_related_staff_for_staff_id(cls, staff_id):
        raise NotImplementedError(
            "Must implement method for retrieving staff sections."
        )

    @classmethod
    def get_source_related_sites_for_staff_id(cls, staff_id):
        """Return { sis_id, name } from source for all sites"""
        return None

    @classmethod
    def get_source_related_terms_for_staff_id(cls, staff_id):
        """Return { sis_id, name, start_date,
            end_date, sis_term_id } from source for all sites"""
        return None

    @classmethod
    def get_source_related_sections_for_staff_id(cls, staff_id):
        """Return { course_name, grade_level, sis_term_id[optional]}"""
        raise NotImplementedError(
            "Must implement method for retrieving staff sections."
        )

    @classmethod
    def get_source_related_staffsectionrecord_for_staff_id(cls, staff_id):
        return None

    @classmethod
    def get_source_related_students_for_staff_id(cls, staff_id):
        raise NotImplementedError(
            "Must implement method for retrieving staff students."
        )

    @classmethod
    def get_source_related_enrollment_records_for_staff_id(cls, staff_id):
        return None

    @classmethod
    def get_source_related_attendance_nodes_for_staff_id(cls, staff_id):
        return None

    @classmethod
    def get_source_related_gradebooks_for_staff_id(cls, staff_id):
        return None

    @classmethod
    def get_source_related_categories_for_staff_id(cls, staff_id):
        return None

    @classmethod
    def get_source_related_assignments_for_staff_id(cls, staff_id):
        return None

    @classmethod
    def get_source_related_scores_for_staff_id(cls, staff_id):
        return None

    def create_all_for_staff(self, source_id):

        id_field = self.source_id_field
        success_string = ""

        model_map = {m.__name__.lower(): m for m in [
            Site, Term, Section, Student, Gradebook,
            Category, Assignment
        ]}

        model_map["user"] = UserProfile

        staff, staff_created = self.get_or_create_staff(source_id)

        if staff_created:
            success_string += f"Staff created for " + \
                              f"{id_field} {source_id}\n"

        # { <model> { <source_id> : <clarify_id> } }
        memoized_related = {}

        def _get_related_model_id(fk_id_field, source_id):
            split_text = fk_id_field.split('_')
            if len(split_text < 3):
                raise ValueError('Improper field format.')

            related_model_name = "".join(split_text[1:-1])

            related_field_key = "".join(split_text[1:])

            if related_model_name in memoized_related and \
               source_id in memoized_related[related_model_name]:
                clarify_id =  memoized_related[related_model_name][source_id]
                return related_field_key, clarify_id

            related_model: Model = model_map[related_model_name]

            clarify_id = (related_model.objects
                                .get(**{id_field: source_id})
                                .id)

            memoized_related[related_model_name][source_id] = clarify_id

            return related_field_key, clarify_id

        def _build_all_models(model: Model, related_query_func,
                              kwargs_list, fk_list=None):
            source_models = related_query_func(source_id)
            count = 0
            import pdb; pdb.set_trace()

            if source_models and len(source_models) > 1:
                for instance in tqdm(source_models,
                                     desc=model.__name__,
                                     leave=False):
                    new_base_kwargs = { k: instance[k] for k in kwargs_list}
                    new_fk_kwargs = {i[0]: i[1] for i in [
                        _get_related_model_id(f, instance[f]) for f in fk_list
                    ]}
                    new_kwargs = {**new_base_kwargs, **new_fk_kwargs}
                    new_instance, created = (model
                                             .objects
                                             .get_or_create(**new_kwargs))

                    if created:
                        count += 1

            pdb.set_trace()

            if count > 0:
                return f"New {model.__name__} instances: {count}\n"

            return ""

        success_string += _build_all_models(
            Site, self.get_source_related_sites_for_staff_id,
            ['name'])

        success_string += _build_all_models(
            Term, self.get_source_related_sites_for_staff_id,
            ['name', 'academic_year', 'start_date','end_date'],
            ['sis_site_id'])

        self.log(success_string)


class IlluminateSync(Sync):

    source_id_field = 'sis_id'

    @classmethod
    def get_source_related_staff_for_staff_id(cls, staff_id):
        return Users.get_staff_values_for_staff_id(staff_id)

    @classmethod
    def get_source_related_sites_for_staff_id(cls, staff_id):
        return Sites.get_current_sites_for_staff_id(staff_id)

    @classmethod
    def get_source_related_terms_for_staff_id(cls, staff_id):
        return Terms.get_current_terms_for_staff_id(staff_id)

    @classmethod
    def get_source_related_sections_for_staff_id(cls, staff_id):
        return Sections.get_current_sections_for_staff_id(staff_id)

    @classmethod
    def get_source_related_staffsectionrecord_for_staff_id(cls, staff_id):
        return Sections.get_current_staff_section_records_for_staff_id(staff_id)

    @classmethod
    def get_source_related_students_for_staff_id(cls, staff_id):
        return Students.get_current_students_for_staff_id(staff_id)

    @classmethod
    def get_source_related_enrollment_records_for_staff_id(cls, staff_id):
        return SectionStudentAff.get_current_enrollment_for_staff_id(staff_id)

    @classmethod
    def get_source_related_gradebooks_for_staff_id(cls, staff_id):
        return Gradebooks.get_current_gradebooks_for_staff_id(staff_id)

    @classmethod
    def get_source_related_categories_for_staff_id(cls, staff_id):
        return Categories.get_current_categories_for_staff_id(staff_id)

    @classmethod
    def get_source_related_assignments_for_staff_id(cls, staff_id):
        return Assignments.get_current_assignments_for_staff_id(staff_id)

    @classmethod
    def get_source_related_scores_for_staff_id(cls, staff_id):
        return ScoreCache.get_current_scores_for_staff_id(staff_id)


class CleverSync(Sync):

    source_id_field = 'clever_id'

    @classmethod
    def get_source_related_sections_for_staff_id(cls, staff_id):
        pass

    @classmethod
    def get_source_related_students_for_staff_id(cls, staff_id):
        pass


