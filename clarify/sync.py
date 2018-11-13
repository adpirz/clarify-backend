from django.contrib.auth.models import User
from django.db.models import Model
from django.utils import timezone

from sis_mirror.models import (
    Students, Users, Sites, AttendanceFlags,
    Sections, Categories, Courses, Gradebooks,
    DailyRecords, GradeLevels, GradebookSectionCourseAff,
    SsCube, SectionTimeblockAff, Timeblocks, SsCurrent,
    Assignments, ScoreCache, Sessions, Terms, UserTermRoleAff
)

from clarify.models import (
    Student,
    Staff,
    Site,
    Term,
    GradeLevel,
    Section,
    EnrollmentRecord,
    StaffSectionRecord,
    DailyAttendanceNode
)


class Sync:
    source_id_field = None

    def __init__(self, logger=None):
        self.logger = logger or print

    def get_or_create_staff(self, source_id, **model_kwargs):
        """
        Create Staff and User if doesn't exist for given source_id
        :param source_id: String; name of source field on Staff
        :param model_kwargs: Dict of user + staff properties
        :return:
        """
        if not Staff.objects.filter(**{
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

            return Staff.objects.create(
                user=user, name=name, prefix=prefix
            ), 1

        # match signature of Model.objects.get_or_create:
        # > Returns a tuple of (object, created)

        return Staff.objects.get(**{
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
    def get_source_related_students_for_staff_id(cls, staff_id):
        raise NotImplementedError(
            "Must implement method for retrieving staff students."
        )


    def create_all_for_staff(self, source_id, **model_kwargs):
        staff, staff_created = self.get_or_create_staff(source_id,
                                                        **model_kwargs)


class IlluminateSync(Sync):

    source_id_field = 'sis_id'

    def get_source_related_sites_for_staff_id(cls, staff_id):
        return Sites.get_users_current_sites(staff_id)

    def get_source_related_terms_for_staff_id(cls, staff_id):
        return Terms.get_current_terms_for_user_id(staff_id)

    def get_source_related_sections_for_staff_id(cls, staff_id):
        return Sections.get_current_sections_for_user_id(staff_id)


