from django.db import models
from django.contrib.auth.models import User

class AttributeNotImplemented()

class SourceObjectMixin:
    """
    Mixin to add source_object_id to a model
    """
    source_object_id = models.PositiveIntegerField()

    def get_source_object_table(self):


    def get_source_object_column(self):
        try:
            return self.source_object_id_column
        except AttributeError:
            raise NotImplementedError(
                f'Class {self.__class__} does not have source_object_id_column.'
            )

    def get_source_schema(self):
        try:
            return


class GradeLevel(SourceObjectMixin, models.Model):
    """
    Source: public.grade_levels
    """
    sort_order = models.IntegerField()
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=455)


class Site(SourceObjectMixin, models.Model):
    """
    Source: public.sites
    Source for site types: public.site_types
    """

    SITE_TYPE_CHOICES = (
        (1, 'Middle and K-8 Schools'),
        (2, 'High Schools'),
        (3, 'Continuation schools'),
        (4, 'Pre-schools'),
        (5, 'Adult Education Facilities'),
        (6, 'Special Education Facilities'),
        (7, 'Other Schools and Facilities'),
        (9, 'Elementary Schools'),
        (10, 'Closed')
    )

    site_name = models.CharField(max_length=255)
    start_grade_level = models.ForeignKey(GradeLevel)
    end_grade_level = models.ForeignKey(GradeLevel)
    site_type = models.IntegerField(choices=SITE_TYPE_CHOICES)
    address = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=100)
    phone2 = models.CharField(max_length=100)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)


class Student(SourceObjectMixin, models.Model):
    """
    Source: public.students
    """

    ETHNICITY_CHOICES = (
        (146, 'Refused to Identify'),
        (141, 'Filipino'),
        (144, 'White'),
        (134, 'Other Asian'),
        (133, 'Cambodian'),
        (132, 'Laotian'),
        (131, 'Asian Indian'),
        (130, 'Vietnamese'),
        (129, 'Korean'),
        (128, 'Japanese'),
        (127, 'Chinese'),
        (145, 'Hmong'),
        (125, 'American Indian Or Alaska Native'),
        (140, 'Other Pacific Islander'),
        (139, 'Tahitian'),
        (138, 'Samoan'),
        (137, 'Guamanian'),
        (136, 'Hawaiian'),
        (143, 'Black or African American'),
    )

    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    ethnicity = models.IntegerField(choices=ETHNICITY_CHOICES)

    def __str__(self):
        return "{}: {}, {}".format(self.pk, self.last_name, self.first_name)


class AttendanceDailyRecord(SourceObjectMixin, models.Model):
    """
    Source: attendance.daily_records
    Source for attendance flags: public.attendance_flags
    """
    ATTENDANCE_FLAG_CHOICES = (
        ('X', 'Not Enrolled'),
        ('N', 'School Closed'),
        ('+', 'Present'),
        ('L', 'Excused tardy'),
        ('M', 'Unexcused Tardy'),
        ('R', 'Early Release'),
        ('E', 'Excused'),
        ('T', 'Tardy'),
        ('U', 'Unexcused'),
        ('Y', 'T30'),
        ('I', 'Independent Study Complete'),
        ('-', 'Independent Study Pending'),
        ('_', 'Independent Study NOT-Complete'),
        ('A', 'Absent'),
        ('D', 'Delete'),
    )

    date = models.DateField()
    site = models.ForeignKey(Site)
    student = models.ForeignKey(Student)
    attendance_flag = models.CharField(max_length=1,
                                       choices=ATTENDANCE_FLAG_CHOICES)

    class Meta:

        unique_together = ('date', 'student')

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

    user = models.OneToOneField(User)
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


class Section(SourceObjectMixin, models.Model):
    """
    Source: public.sections
    """
    section_name = models.CharField(max_length=255)


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


class CategoryType(SourceObjectMixin, models.Model):
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


class GradebookSectionCourseAffinity(SourceObjectMixin, models.Model):
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
