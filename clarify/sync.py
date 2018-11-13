from django.contrib.auth.models import User
from django.db.models import Model
from django.utils import timezone

from sis_mirror.models import (
    Sites,
    Terms,
    Students,
    Sections,
    SectionStudentAff,
    Gradebooks,
    Categories,
    Assignments,
    ScoreCache
)

from clarify.models import (
    Student,
    UserProfile,
    Site,
    Term,
    Section,
    EnrollmentRecord,
    StaffSectionRecord,
    DailyAttendanceNode
)


class Sync:
    source_id_field = None

    def __init__(self, logger=None, enable_logging=True):
        self.logger = (logger or print) if enable_logging else None

    def log(self, *args, **kwargs):
        if self.logger:
            return self.logger(*args, **kwargs)

        return None

    def get_or_create_staff(self, source_id, **model_kwargs):
        """
        Create Staff and User if doesn't exist for given source_id
        :param source_id: String; name of source field on Staff
        :param model_kwargs: Dict of user + staff properties
        :return:
        """
        if not UserProfile.objects.filter(**{
            self.source_id_field: source_id
        }).exists():
            email = model_kwargs["email"]
            first_name = model_kwargs.get("first_name", "")
            last_name = model_kwargs.get("last_name", "")
            user = User.objects.create(
                email=email, first_name=first_name, last_name=last_name
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
            self.source_id_field: source_id
        }), 0

    """ All methods below pull only current records """

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

    def create_all_for_staff(self, source_id, **model_kwargs):
        staff, staff_created = self.get_or_create_staff(source_id,
                                                        **model_kwargs)


class IlluminateSync(Sync):

    source_id_field = 'sis_id'

    def get_source_related_sites_for_staff_id(cls, staff_id):
        return Sites.get_current_sites_for_staff_id(staff_id)

    def get_source_related_terms_for_staff_id(cls, staff_id):
        return Terms.get_current_terms_for_staff_id(staff_id)

    def get_source_related_sections_for_staff_id(cls, staff_id):
        return Sections.get_current_sections_for_staff_id(staff_id)

    def get_source_related_staffsectionrecord_for_staff_id(cls, staff_id):
        return Sections.get_current_staff_section_records_for_staff_id(staff_id)

    def get_source_related_students_for_staff_id(cls, staff_id):
        return Students.get_current_students_for_staff_id(staff_id)

    def get_source_related_enrollment_records_for_staff_id(cls, staff_id):
        return SectionStudentAff.get_current_enrollment_for_staff_id(staff_id)

    def get_source_related_gradebooks_for_staff_id(cls, staff_id):
        return Gradebooks.get_current_gradebooks_for_staff_id(staff_id)

    def get_source_related_categories_for_staff_id(cls, staff_id):
        return Categories.get_current_categories_for_staff_id(staff_id)

    def get_source_related_assignments_for_staff_id(cls, staff_id):
        return Assignments.get_current_assignments_for_staff_id(staff_id)

    def get_source_related_scores_for_staff_id(cls, staff_id):
        return ScoreCache.get_current_scores_for_staff_id(staff_id)


class CleverSync(Sync):

    source_id_field = 'clever_id'

    def get_source_related_sections_for_staff_id(cls, staff_id):
        pass

    def get_source_related_students_for_staff_id(cls, staff_id):
        pass


