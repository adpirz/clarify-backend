from django.db import models
from clarify_backend.settings.base import AUTH_USER_MODEL


class SourceObjectMixin:
    source_object_id = models.PositiveIntegerField()


class Site(SourceObjectMixin, models.Model):
    pass


class Ethnicity(SourceObjectMixin, models.Model):
    code_id = models.IntegerField()
    code_key = models.CharField(max_length=10)
    code_translation = models.CharField(max_length=255)

    class Meta:
        source_object_table = 'dog'


class Student(SourceObjectMixin, models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    ethnicity = models.ForeignKey(Ethnicity)

    def __str__(self):
        return "{}: {}, {}".format(self.pk, self.last_name, self.first_name)


class AttendanceFlag(SourceObjectMixin, models.Model):
    flag_text = models.CharField(max=255)
    character_code = models.CharField(max=30)


class AttendanceDailyRecord(SourceObjectMixin, models.Model):

    date = models.DateField()
    student = models.ForeignKey(Student)
    attendance_flag = models.ForeignKey(AttendanceFlag)

    class Meta:

        unique_together = ('school_day', 'student')

    def __str__(self):
        return f"{self.school_day}: {self.student} - {self.code}"


class Staff(SourceObjectMixin, models.Model):

    PREFIX_CHOICES = (
        ('MR', 'Mr.'),
        ('MS', 'Ms.'),
        ('MRS', 'Mrs.')
    )

    user = models.OneToOneField(AUTH_USER_MODEL)
    prefix = models.CharField(choices=PREFIX_CHOICES, max_length=3, default='MS')

    def __str__(self):
        return "{} {} {}".format(self.get_prefix_display(),
                                 self.user.first_name,
                                 self.user.last_name)

    class Meta:
        verbose_name = 'staff'
        verbose_name_plural = verbose_name


class Course(SourceObjectMixin, models.Model):
    short_name = models.CharField(max_length=30)
    long_name = models.CharField(max_length=255)
    description = models.TextField()
    school_course_id = models.CharField(max_length=20)
    site_id = models.ForeignKey(Site)
    is_active = models.BooleanField(default=True)
    models.
    pass


class GradeLevel(SourceObjectMixin, models.Model):
    pass


class SectionLevelRosterPerYear(models.Model):
    site_id = models.ForeignKey(Site)
    academic_year = models.PositiveIntegerField()
    grade_level_id = models.ForeignKey(GradeLevel)
    user_id = models.ForeignKey(Staff)
    section_id = models.ForeignKey(Staff)
    course_id = models.ForeignKey(Course)