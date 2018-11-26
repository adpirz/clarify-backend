from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db.models import Model
from django.utils import timezone
from tqdm import tqdm

from clarify import models
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
    Gradebook, Category, Assignment, Score, SectionGradeLevels)


class Sync:
    source_id_field = None

    def __init__(self, logger=None, enable_logging=True):
        self.logger = (logger or print) if enable_logging else None
        self.memoized_related = {}

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
        id_field = cls.source_id_field
        if not (UserProfile.objects
                .filter(**{id_field: source_id})
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
                user=user, name=name, prefix=prefix, **{id_field: source_id}
            ), 1

        # match signature of Model.objects.get_or_create:
        # > Returns a tuple of (object, created)

        return UserProfile.objects.get(**{
            id_field: source_id
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

    @classmethod
    def get_all_current_staff_ids_from_source(cls):
        return None

    def create_all_for_staff(self, staff_id):

        return_dict = {}

        id_field = self.source_id_field
        success_string = ""

        model_map = {m.__name__.lower(): m for m in [
            Site, Term, Section, Student, Gradebook,
            Category, Assignment
        ]}

        model_map["user"] = UserProfile

        staff, staff_created = self.get_or_create_staff(staff_id)

        if staff_created:
            success_string += f"Staff created for " + \
                              f"{id_field} {staff_id}\n"

        # { <model> { <source_id> : <clarify_id> } }
        memoized_related = self.memoized_related

        def _get_related_model_id(fk_id_field, source_id):
            if not source_id:
                return None

            split_text = fk_id_field.split('_')
            if len(split_text) < 3:
                raise ValueError('Improper field format.')

            related_model_name = "".join(split_text[1:-1])

            related_field_key = "_".join(split_text[1:])

            if related_model_name in memoized_related and \
               source_id in memoized_related[related_model_name]:
                clarify_id = memoized_related[related_model_name][source_id]
                return related_field_key, clarify_id

            related_model: Model = model_map[related_model_name]

            try:
                clarify_id = (related_model.objects
                                           .get(**{id_field: source_id})
                                           .id)
            except related_model.DoesNotExist:
                return None

            if related_model_name not in memoized_related:
                memoized_related[related_model_name] = {}

            memoized_related[related_model_name][source_id] = clarify_id

            return related_field_key, clarify_id

        def _build_all_models(model: Model, related_query_func,
                              kwargs_list, fk_list=None):

            source_models = related_query_func(staff_id)
            count = 0
            errors = 0

            if source_models and len(source_models) > 0:

                if len(source_models) > 40:
                    iterator = tqdm(source_models,
                                     desc=model.__name__,
                                     leave=False)
                else:
                    iterator = source_models

                for instance in iterator:
                    new_kwargs = {
                        k: instance.get(k) for k in kwargs_list
                    }

                    if model is Section and not instance.get('name'):
                        new_kwargs["name"] = f"{instance.get('period')} " + \
                                             f"{instance.get('course_name')}"

                    if fk_list:
                        fk_tuple = filter(
                            lambda x: x is not None,
                            [_get_related_model_id(f, instance.get(f))
                             for f in fk_list]
                        )

                        new_fk_kwargs = {i[0]: i[1] for i in fk_tuple}
                        new_kwargs.update(new_fk_kwargs)

                    try:
                        new_instance, created = (model
                                             .objects
                                             .get_or_create(**new_kwargs))
                    except (model.MultipleObjectsReturned, IntegrityError):
                        new_instance, created = (None, None)
                        errors += 1

                    if created:
                        count += 1

                    if (isinstance(new_instance, Gradebook) and
                       not new_instance.owners.filter(pk=staff_id).exists()):
                        new_instance.owners.add(staff_id)

                    if (isinstance(new_instance, Section) and
                            not new_instance.sectiongradelevels_set.exists()
                            and instance.get('grade_level')):
                        SectionGradeLevels.objects.create(
                            grade_level=instance.get('grade_level'),
                            section=new_instance
                        )
            return count, errors

        build_args = [
            (Site, self.get_source_related_sites_for_staff_id,
                ['sis_id', 'name']),
            (Term, self.get_source_related_terms_for_staff_id,
                ['sis_id', 'name', 'academic_year', 'start_date', 'end_date'],
                ['sis_site_id']),
            (Section, self.get_source_related_sections_for_staff_id,
                ['sis_id', 'name', 'course_name'],
                ['sis_term_id']),
            (Student, self.get_source_related_students_for_staff_id,
                ['sis_id', 'first_name', 'last_name']),
            (EnrollmentRecord,
                self.get_source_related_enrollment_records_for_staff_id,
                ['start_date', 'end_date'],
                ['sis_student_id', 'sis_section_id']),
            (Gradebook, self.get_source_related_gradebooks_for_staff_id,
                ['sis_id', 'name'],
                ['sis_section_id']),
            (Category, self.get_source_related_categories_for_staff_id,
                ['sis_id', 'name'],
                ['sis_gradebook_id']),
            (Assignment, self.get_source_related_assignments_for_staff_id,
                ['sis_id', 'name', 'possible_points', 'possible_score'],
                ['sis_gradebook_id', 'sis_category_id']),
            (Score, self.get_source_related_scores_for_staff_id,
                ['sis_id', 'score', 'value', 'is_missing', 'is_excused'],
                ['sis_student_id', 'sis_assignment_id'])
        ]

        for arg_set in build_args:
            new_count, new_errors = _build_all_models(*arg_set)
            model_name = arg_set[0].__name__

            if new_count > 0 or new_errors > 0:
                return_dict[model_name] = [new_count, new_errors]

        return return_dict


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

    @classmethod
    def get_all_current_staff_ids_from_source(cls):
        return Users.get_all_current_staff_ids()

    def create_all_for_current_staff(self, staff_id_list=None,
                                     # used for rapid testing
                                     sparse=False):
        total_result_dict = {}

        staff_ids = staff_id_list if staff_id_list else \
            self.get_all_current_staff_ids_from_source()

        if sparse:
            staff_ids = staff_ids[::20]

        for staff_id in tqdm(staff_ids, desc="Staff"):
            result_dict = self.create_all_for_staff(staff_id)
            for model_name, outcome_list in result_dict.items():
                if model_name not in total_result_dict:
                    total_result_dict[model_name] = outcome_list
                else:
                    total_result_dict[model_name][0] += outcome_list[0]
                    total_result_dict[model_name][1] += outcome_list[1]

        return total_result_dict


class CleverSync(Sync):

    source_id_field = 'clever_id'

    @classmethod
    def get_source_related_sections_for_staff_id(cls, staff_id):
        pass

    @classmethod
    def get_source_related_students_for_staff_id(cls, staff_id):
        pass


