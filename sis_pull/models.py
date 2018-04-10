from django.db import models
from clarify_backend.settings.base import AUTH_USER_MODEL


class SourceObjectMixin:
    """
    Mixin to add source_object_id to a model
    """
    source_object_id = models.PositiveIntegerField()


class Site(SourceObjectMixin, models.Model):
    """
    Source: public.sites
    """
    pass


class Ethnicity(SourceObjectMixin, models.Model):
    """
    Source: public.ethnicity
    """
    code_id = models.IntegerField()
    code_key = models.CharField(max_length=10)
    code_translation = models.CharField(max_length=255)


class Student(SourceObjectMixin, models.Model):
    """
    Source: public.students
    """
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    ethnicity = models.ForeignKey(Ethnicity)

    def __str__(self):
        return "{}: {}, {}".format(self.pk, self.last_name, self.first_name)


class AttendanceFlag(SourceObjectMixin, models.Model):
    """
    Source: public.attendance_flags
    """
    flag_text = models.CharField(max=255)
    character_code = models.CharField(max=30)


class AttendanceDailyRecord(SourceObjectMixin, models.Model):
    """
    Source: attendance.daily_records
    """
    date = models.DateField()
    student = models.ForeignKey(Student)
    attendance_flag = models.ForeignKey(AttendanceFlag)

    class Meta:

        unique_together = ('school_day', 'student')

    def __str__(self):
        return f"{self.school_day}: {self.student} - {self.code}"


class Staff(SourceObjectMixin, models.Model):
    """
    Source: public.users
    """

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
    """
    Source: public.courses
    """
    short_name = models.CharField(max_length=30)
    long_name = models.CharField(max_length=255)
    description = models.TextField()
    school_course_id = models.CharField(max_length=20)
    site_id = models.ForeignKey(Site)
    is_active = models.BooleanField(default=True)
    pass


class GradeLevel(SourceObjectMixin, models.Model):
    """
    Source: public.grade_levels
    """
    sort_order = models.IntegerField()
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=455)
    pass


class Section(SourceObjectMixin, models.Model):
    """
    Source: public.sections
    """
    pass


class SectionLevelRosterPerYear(SourceObjectMixin, models.Model):
    """
    Source: matviews.ss_cube
    * Key through-table to everything
    """
    site = models.ForeignKey(Site)
    academic_year = models.PositiveIntegerField()
    grade_level = models.ForeignKey(GradeLevel)
    user = models.ForeignKey(Staff)
    section = models.ForeignKey(Section)
    course = models.ForeignKey(Course)


class Gradebook(SourceObjectMixin, models.Model):
    """
    Source: gradebook.gradebooks
    """
    created_on = models.DateTimeField()
    created_by = models.ForeignKey(Staff)
    gradebook_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    academic_year = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)


class CategoryType(SourceObjectMixin, models):
    """
    Source gradebook.category_types
    """
    category_type_name = models.CharField(max_length=255)
    is_academic = models.BooleanField(default=True)


class Category(SourceObjectMixin, models.Model):
    """
    Source: gradebook.categories
    """
    category_name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    gradebook = models.ForeignKey(Gradebook)
    weight = models.FloatField()
    category_type = models.ForeignKey(CategoryType)


class GradebookSectionCourseAff(SourceObjectMixin, models.Model):
    """
    Source: gradebook.gradebook_section_course_aff
    """
    gradebook = models.ForeignKey(Gradebook)
    section = models.ForeignKey(Section)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(Staff)
    created = models.DateTimeField()
    modified = models.DateTimeField()


class OverallScoreCache(SourceObjectMixin, models.Model):
    """
    Source: gradebook.overall_score_cache

    * This is our go-to for gradebook scores
    """
    student = models.ForeignKey(Student)
    gradebook = models.ForeignKey(Gradebook)
    possible_points = models.FloatField()
    points_earned = models.FloatField()
    percentage = models.FloatField()
    mark = models.CharField(max_length=255)
    missing_count = models.IntegerField()
    zero_count = models.IntegerField()
    excused_count = models.IntegerField()


class CategoryScoreCache(SourceObjectMixin, models.Model):
    """
    Source: gradebook.category_score_cache
    """
    student = models.ForeignKey(Student)
    gradebook = models.ForeignKey(Gradebook)
    category = models.ForeignKey(Category)
    possible_points = models.FloatField()
    points_earned = models.FloatField()
    percentage = models.FloatField()
    category_name = models.CharField(max_length=255)
    mark = models.CharField(max_length=255)
    assignment_count = models.IntegerField()
    calculated_at = models.DateTimeField()
    timeframe_start_date = models.DateField()
    timeframe_end_date = models.DateField()