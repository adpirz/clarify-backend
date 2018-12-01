from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models

from django.db.models import Q, F
from django.utils import timezone

"""

Abstract Base Models

"""


class CleverIDMixin (models.Model):
    clever_id = models.CharField(max_length=50, unique=True, null=True)

    class Meta:
        abstract = True


class SISMixin(models.Model):
    sis_id = models.BigIntegerField(null=True)

    class Meta:
        abstract = True


class NameInterface:

    def get_full_name(self):
        raise NotImplementedError('Must implement get_full_name')

    def get_first_name(self):
        raise NotImplementedError('Must implement get_first_name')

    def get_last_name(self):
        raise NotImplementedError('Must implement get_last_name')


class BaseNameModel(CleverIDMixin, SISMixin):

    name = models.CharField(max_length=255)

    class Meta:
        abstract = True


"""

Concrete Models

"""

# This is akin to a Staff or Teacher object in Clever and SISs.
class UserProfile(NameInterface, SISMixin, CleverIDMixin):
    PREFIX_CHOICES = (
        ('MR', 'Mr.'),
        ('MS', 'Ms.'),
        ('MRS', 'Mrs.'),
    )

    name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User)
    prefix = models.CharField(max_length=3,
                              choices=PREFIX_CHOICES,
                              blank=True)
    clever_token = models.CharField(max_length=300, null=True)

    def get_full_mame(self):
        if len(self.user.first_name) and len(self.user.last_name):
            return f"{self.user.first_name} {self.user.last_name}"
        if len(self.user.first_name):
            return self.user.first_name
        if len(self.user.last_name):
            return self.user.last_name
        if len(self.name):
            return self.name

    def get_first_name(self):
        return self.user.first_name

    def get_last_name(self):
        return self.user.last_name

    def get_current_sections(self):
        return StaffSectionRecord.objects.filter(
            Q(start_date__lte=timezone.now()) | Q(start_date__isnull=True),
            Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True),
            active=True,
            user_profile_id=self.id,
        ).distinct('section_id')


    def get_enrolled_students(self):

        student_section_teacher_id = "__".join([
            "enrollmentrecord", "section", "staffsectionrecord", "user_profile_id"
        ])

        enrolled_now = (
            Q(enrollmentrecord__start_date__lte=timezone.now()) |
            Q(enrollmentrecord__start_date__isnull=True),
            Q(enrollmentrecord__end_date__gte=timezone.now()) |
            Q(enrollmentrecord__end_date__isnull=True),
        )

        return (
            Student.objects
                .filter(
                **{student_section_teacher_id: self.id})
                .filter(*enrolled_now)
                .annotate(section_id=F("enrollmentrecord__section_id"))
                .distinct('id', 'section_id')
        )



class CleverCode(models.Model):
    code = models.CharField(max_length=250, unique=True)
    user_profile = models.ForeignKey(UserProfile, null=True)


class Student(NameInterface, CleverIDMixin, SISMixin):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)

    name = models.CharField(max_length=200, blank=True)

    def get_full_name(self):
        if len(self.first_name) and len(self.last_name):
            return f"{self.first_name} {self.last_name}"
        if len(self.first_name):
            return self.first_name
        if len(self.last_name):
            return self.last_name
        if len(self.name):
            return self.name

        raise AttributeError("No name provided.")

    def get_first_name(self):
        return self.FIRST_NAME

    def get_last_name(self):
        return self.last_name

    # Adding this so that the django admin presents Students more intelligbly
    def __str__(self):
        return self.get_full_name()


class Site(BaseNameModel):
    pass


class Term(BaseNameModel):
    # latter year; eg. 2019 represents '18 - '19 school year
    academic_year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    site = models.ForeignKey(Site)

    @classmethod
    def current_terms_qs(cls):
        return cls.objects.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

    def get_section_ids(self):
        return Section.objects.filter(
            term_id=self.id
        ).values_list('section_id', flat=True)


class Section(BaseNameModel):

    course_name = models.CharField(max_length=255, blank=True, null=True)
    term = models.ForeignKey(Term, null=True)


class SectionGradeLevels(models.Model):
    """Allows for multiple choice grade levels per section"""
    GRADE_LEVEL_CHOICES = (
        ('PK', 'Pre-Kindergarten'),
        ('K', 'Kindergarten'),
        ('1', '1st Grade'),
        ('2', '2nd Grade'),
        ('3', '3rd Grade'),
        ('4', '4th Grade'),
        ('5', '5th Grade'),
        ('6', '6th Grade'),
        ('7', '7th Grade'),
        ('8', '8th Grade'),
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade'),
    )

    # Grade levels should be Clarify standardized
    grade_level = models.CharField(max_length=2, choices=GRADE_LEVEL_CHOICES)
    section = models.ForeignKey(Section)


class EnrollmentRecord(models.Model):
    student = models.ForeignKey(Student)
    section = models.ForeignKey(Section)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    class Meta:
        unique_together = ('student', 'section')


class StaffSectionRecord(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    section = models.ForeignKey(Section)
    # catch all that determines if this is current
    active = models.BooleanField(default=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    primary_teacher = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user_profile', 'section')


class StaffAdminRecord(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    term = models.ForeignKey(Term)


class DailyAttendanceNode(models.Model):
    """Works for daily level attendance, not section level attendance"""
    FLAG_CHOICES = (
        # Kept 'P', 'T', and 'A' as catch-alls
        # for present, tardy, and absent codes
        # not quantified here

        ('P', 'Present'),
        ('T', 'Tardy'),
        ('TE', 'Tardy Excused'),
        ('TU', 'Tardy Unexcused'),
        ('A', 'Absent'),
        ('AE', 'Absent Excused'),
        ('AU', 'Absent Unexcused'),
    )

    date = models.DateField()
    student = models.ForeignKey(Student)
    flag = models.CharField(max_length=2, choices=FLAG_CHOICES)

    class Meta:
        unique_together = ('date', 'student')


class Gradebook(BaseNameModel):
    section = models.ForeignKey(Section)
    # Some gradebooks have multiple owners / viewers
    owners = models.ManyToManyField(UserProfile)

    @classmethod
    def get_all_current_gradebook_ids_for_user_profile(cls, profile_id):
        return (cls.objects
                .filter(owners__id=profile_id)
                .distinct('id')
                .values_list('id', flat=True))


class Category(BaseNameModel):
    gradebook = models.ForeignKey(Gradebook)


class Assignment(BaseNameModel):
    # in case category doesn't exist, we keep
    # a gradebook record on the assignment
    gradebook = models.ForeignKey(Gradebook)
    category = models.ForeignKey(Category, null=True)

    # TODO: Which goes into final grade?
    possible_points = models.FloatField(null=True)
    possible_score = models.FloatField(null=True)

    due_date = models.DateField(null=True)


class Score(SISMixin):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)

    # Nullable if excused
    score = models.FloatField(null=True)
    value = models.FloatField(null=True)

    is_missing = models.BooleanField(default=False)
    is_excused = models.BooleanField(default=False)

    updated_on = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('student', 'assignment')

