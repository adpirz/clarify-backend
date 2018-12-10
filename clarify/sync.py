import re
import requests
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db.models import Model
from django.utils import timezone
from pprint import pprint
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
from clarify_backend.utils.utils import try_bulk_or_skip_errors


class Sync:
    source_id_field = None
    model_args_map = None

    def __init__(self, logger=None, enable_logging=True):
        self.logger = (logger or print) if enable_logging else None

    def log(self, *args, **kwargs):
        if self.logger:
            return self.logger(*args, **kwargs)

        return None

    def get_model_query_func(self, clarify_model):
        # Instance function in case
        # subclasses implement an instance
        # method for any of the functions

        query_map = {
            Site: self.get_source_related_sites_for_staff_id,
            Term: self.get_source_related_terms_for_staff_id,
            Section: self.get_source_related_sections_for_staff_id,
            Student: self.get_source_related_students_for_staff_id,
            EnrollmentRecord: self.get_source_related_enrollment_records_for_staff_id,
            Gradebook: self.get_source_related_gradebooks_for_staff_id,
            Category: self.get_source_related_categories_for_staff_id,
            Assignment: self.get_source_related_assignments_for_staff_id,
            Score: self.get_source_related_scores_for_staff_id
        }

        return query_map.get(clarify_model, None)

    def get_or_create_staff(self, source_id):
        """
        Create Staff and User if doesn't exist for given source_id
        :param source_id: String; name of source field on Staff
        :param model_kwargs: Dict of user + staff properties
        :return:
        """
        id_field = self.source_id_field
        if not (UserProfile.objects
                .filter(**{id_field: source_id})
                .exists()):

            model_kwargs = self.get_source_related_staff_for_staff_id(source_id)
            email = model_kwargs.get("email", "")
            first_name = model_kwargs.get("first_name", "")
            last_name = model_kwargs.get("last_name", "")
            username = model_kwargs.get("username", None) or email
            user = User.objects.create(
                username=username, email=email,
                first_name=first_name, last_name=last_name
            )
            # We don't want passwords blank or folks can sign in willy nilly, plus the admin form
            # comlains when we save Users without passworsd.
            user.set_password(User.objects.make_random_password())

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

    def create_all_for_staff_from_source(self, source_id):

        return_dict = {}

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

            source_models = related_query_func(source_id)
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
                       not new_instance.owners.filter(pk=source_id).exists()):
                        new_instance.owners.add(source_id)

                    if (isinstance(new_instance, Section) and
                            not new_instance.sectiongradelevels_set.exists()
                            and instance.get('grade_level')):
                        SectionGradeLevels.objects.create(
                            grade_level=instance.get('grade_level'),
                            section=new_instance
                        )
            return count, errors

        for model, model_args in self.model_args_map.items():
            query_func = self.get_model_query_func(model)
            args = [model, query_func] + list(model_args)
            new_count, new_errors = _build_all_models(*args)
            model_name = model.__name__

            if new_count > 0 or new_errors > 0:
                return_dict[model_name] = [new_count, new_errors]

        return return_dict


class IlluminateSync(Sync):

    source_id_field = 'sis_id'
    model_args_map = {
        Site: (['sis_id', 'name'],),
        Term: (['sis_id', 'name', 'academic_year', 'start_date', 'end_date'],
                ['sis_site_id']),
        Section: (['sis_id', 'name', 'course_name'],
                ['sis_term_id']),
        Student: (['sis_id', 'first_name', 'last_name'],),
        EnrollmentRecord: (['start_date', 'end_date'],
                           ['sis_student_id', 'sis_section_id']),
        Gradebook: (['sis_id', 'name'],
                    ['sis_section_id']),
        Category: (['sis_id', 'name'],
                   ['sis_gradebook_id']),
        Assignment: (['sis_id', 'name', 'possible_points', 'possible_score'],
                     ['sis_gradebook_id', 'sis_category_id']),
        Score: (['sis_id', 'score', 'value', 'is_missing',
                 'is_excused', 'updated_on'],
                ['sis_student_id', 'sis_assignment_id'])
    }

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
            result_dict = self.create_all_for_staff_from_source(staff_id)
            for model_name, outcome_list in result_dict.items():
                if model_name not in total_result_dict:
                    total_result_dict[model_name] = outcome_list
                else:
                    total_result_dict[model_name][0] += outcome_list[0]
                    total_result_dict[model_name][1] += outcome_list[1]

        return total_result_dict


class CleverSync(Sync):
    model_args_map = {
        Site: (['clever_id', 'name'],),
        Term: (['clever_id', 'name', 'academic_year', 'start_date', 'end_date'],
               ['clever_site_id']),
        Section: (['clever_id', 'name', 'course_name'],
                  ['clever_term_id']),
        Student: (['clever_id', 'first_name', 'last_name'],),
        EnrollmentRecord: (['start_date', 'end_date'],
                           ['clever_student_id', 'clever_section_id'])
    }

    source_id_field = 'clever_id'
    base_url = "https://api.clever.com"

    def __init__(self, token=None, staff_id=None):
        Sync.__init__(self)
        self.token = token
        self.staff_id = staff_id
        self._teacher_id = None

        # { clever_id: (<Section>, grade_level_string) }
        self.sections = {}

        # { clever_id: <Student> }
        self.students = {}

    @property
    def teacher_id(self):
        if self._teacher_id:
            return self._teacher_id
        if self.staff_id:
            teacher_id = self\
                .get_source_related_staff_for_staff_id(self.staff_id)["id"]
            self._teacher_id = teacher_id
            return teacher_id
        return None

    @teacher_id.setter
    def teacher_id(self, teacher_id):
        self._teacher_id = teacher_id

    @classmethod
    def build_url(cls, resource_string):
        resource_formatted = resource_string if resource_string[0] == '/' \
            else '/' + resource_string
        if re.match(r'/v\d\.\d/', resource_string):
            return cls.base_url + resource_formatted
        return cls.base_url + '/v2.0' + resource_formatted

    def get_resource_from_clever_api(self, resource_string):
        if not self.token:
            raise AttributeError("No token for auth.")

        resource = requests.get(self.build_url(resource_string),
                            headers={
                                "Authorization": f"Bearer {self.token}"
                            })
        resource.raise_for_status()
        return resource.json()

    def get_source_related_staff_for_staff_id(self, source_id):
        if not self.token:
            raise AttributeError("No token for auth.")

        me = requests.get(self.build_url('/me'),
                          headers={
                              "Authorization": f"Bearer {self.token}"
                          })
        me = me.json()

        self.teacher_id = me["data"]["id"]

        url = me["links"][1]["uri"]

        return self.get_resource_from_clever_api(url)["data"]

    def get_source_related_sections_for_staff_id(self, staff_id):
        if not self.teacher_id:
            raise AttributeError("Need a teacher ID")

        sections_data = self.get_resource_from_clever_api(
            f"/teachers/{self.teacher_id}/sections"
        )["data"]

        sections = []
        for section_data in sections_data:
            data = section_data["data"]
            clever_id = data.get("id", "")
            name = data.get("name", "")
            course_name = name.split(" - ")[0]
            section_tuple = (Section(
                name=name,
                course_name=course_name,
                clever_id=clever_id
            ), data["grade"], data["students"])
            sections.append(section_tuple)
            self.sections[clever_id] = section_tuple

        return sections

    def get_source_related_students_for_staff_id(self, staff_id):
        if not self.teacher_id:
            raise AttributeError("Need a teacher ID")

        if not self.sections:
            self.get_source_related_sections_for_staff_id(staff_id)

        students_data = []

        for section_id in self.sections.keys():
            students_data += self.get_resource_from_clever_api(
                f"/sections/{section_id}/students"
            )["data"]

        students = []
        for student_data in students_data:
            data = student_data["data"]
            clever_id = data["id"]
            first_name = data["name"]["first"]
            last_name = data["name"]["last"]
            new_student = Student(
                first_name=first_name,
                last_name=last_name,
                clever_id=clever_id
            )
            self.students[clever_id] = new_student
            students.append(new_student)

        return students

    def create_all_for_staff_from_source(self, source_id):

        new, errors = 0, 0

        user_profile = self.get_or_create_staff(source_id)[0]
        self.get_source_related_staff_for_staff_id(user_profile.id)

        if not self.sections:
            self.get_source_related_sections_for_staff_id(source_id)

        if not self.students:
            self.get_source_related_students_for_staff_id(source_id)

        sections = [s[0] for s in self.sections.values()]

        sec_new, sec_err = try_bulk_or_skip_errors(Section, sections)

        stu_new, stu_err = try_bulk_or_skip_errors(Student,
                                                   self.students.values())

        self.log(f"SECTION NEW: {sec_new}, SECTION ERR: {sec_err}")
        self.log(f"STUDENT NEW: {stu_new}, STUDENT ERR: {stu_err}")

        for section, grade_level, clever_student_ids in self.sections.values():
            if section.id:
                StaffSectionRecord.objects.get_or_create(
                    user_profile=user_profile,
                    section=section,
                    active=True
                )

            enrollments = []
            for clever_student_id in clever_student_ids:
                student_id = self.students[clever_student_id].id
                enrollments.append(
                    EnrollmentRecord(
                        student_id=student_id,
                        section_id=section.id
                    )
                )

            enr_new, enr_err = try_bulk_or_skip_errors(EnrollmentRecord,
                                                       enrollments)
            self.log(f"ENROLLMENTS NEW: {enr_new}, ENROLLMENTS ERR: {enr_err}")







