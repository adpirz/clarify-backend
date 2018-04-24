from django.db import models
from django.contrib.auth.models import User


class SourceObjectMixin(models.Model):
    """
    Mixin to add source_object_id to a model
    Should implement source_object_table;
    If schema not 'public', should implement source_object_schema
    """
    source_object_id = models.PositiveIntegerField(null=True, unique=True)

    @property
    def source_table(self):
        return self.source_object_table

    @property
    def source_schema(self):
        if self.source_object_schema:
            return self.source_object_schema
        return 'public'

    @property
    def source_args(self):
        """
        Convenience method for source table args
        :return: Tuple (schema, table, id)
        """
        return self.source_schema, self.source_table, self.source_object_id

    class Meta:
        abstract = True


class GradeLevel(SourceObjectMixin):
    """
    Source: public.grade_levels
    """
    source_object_table = 'grade_levels'

    sort_order = models.IntegerField()
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=455, null=True)

    def get_current_students(self, site=None):
        pass


class Site(SourceObjectMixin):
    """
    Source: public.sites
    Source for site types: public.site_types
    """
    source_object_table = 'sites'

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
    start_grade_level = models.ForeignKey(GradeLevel,
                                          related_name='start_grade_level')
    end_grade_level = models.ForeignKey(GradeLevel,
                                        related_name='end_grade_level')
    site_type_id = models.IntegerField(choices=SITE_TYPE_CHOICES)
    address = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=100)
    phone2 = models.CharField(max_length=100)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)

    def get_site_type_label(self):
        return self.SITE_TYPE_CHOICES[self.site_type_id][1]


class Student(SourceObjectMixin):
    """
    Source: public.students
    """

    source_object_table = 'students'

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

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    ethnicity = models.IntegerField(choices=ETHNICITY_CHOICES, null=True)

    def __str__(self):
        return "{}: {}, {}".format(self.pk, self.last_name, self.first_name)


class AttendanceFlag(SourceObjectMixin):
    source_object_table = "attendance_flag"

    character_code = models.CharField(max_length=30, blank=True)
    flag_text = models.CharField(max_length=255, blank=True, null=True)


class AttendanceDailyRecord(SourceObjectMixin):
    """
    Source: attendance.daily_records
    Source for attendance flags: public.attendance_flags
    """
    source_object_table = 'daily_records'
    source_object_schema = 'attendance'

    date = models.DateField()
    site = models.ForeignKey(Site)
    student = models.ForeignKey(Student)
    attendance_flag = models.ForeignKey(AttendanceFlag)

    def __str__(self):
        return f"{self.school_day}: {self.student} - {self.code}"


class Staff(SourceObjectMixin):
    """
    Source: public.users
    """
    source_object_table = 'users'

    PREFIX_CHOICES = (
        ('MR', 'Mr.'),
        ('MS', 'Ms.'),
        ('MRS', 'Mrs.')
    )

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    user = models.OneToOneField(User)
    prefix = models.CharField(choices=PREFIX_CHOICES, max_length=3, default='MS')
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(self.get_prefix_display(),
                                 self.user.first_name,
                                 self.user.last_name)

    class Meta:
        verbose_name = 'staff'
        verbose_name_plural = verbose_name


class Course(SourceObjectMixin):
    """
    Source: public.courses
    """
    source_object_table = 'courses'

    short_name = models.CharField(max_length=30)
    long_name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    school_course_id = models.CharField(max_length=20, null=True)
    site_id = models.ForeignKey(Site)
    is_active = models.BooleanField(default=True)


class Section(SourceObjectMixin):
    """
    Source: public.sections
    """
    source_object_table = 'sections'

    section_name = models.CharField(max_length=255, null=True)


class SectionLevelRosterPerYear(SourceObjectMixin):
    """
    Source: matviews.ss_cube
    * Key through-table to everything
    """
    source_object_table = 'ss_cube'
    source_object_schema = 'matviews'

    site = models.ForeignKey(Site)
    academic_year = models.PositiveIntegerField()
    grade_level = models.ForeignKey(GradeLevel)
    user = models.ForeignKey(Staff)
    section = models.ForeignKey(Section)
    course = models.ForeignKey(Course)
    student= models.ForeignKey(Student)
    entry_date = models.DateField(null=True)
    leave_date = models.DateField(null=True)
    is_primary_teacher = models.NullBooleanField()


class Gradebook(SourceObjectMixin):
    """
    Source: gradebook.gradebooks
    """
    source_object_table = 'gradebooks'
    source_object_schema = 'gradebook'

    created_on = models.DateTimeField()
    created_by = models.ForeignKey(Staff)
    gradebook_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    academic_year = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)


class Category(SourceObjectMixin):
    """
    Source: gradebook.categories
    """
    source_object_table = 'categories'
    source_object_schema = 'gradebook'

    category_name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    gradebook = models.ForeignKey(Gradebook)
    weight = models.FloatField()


class GradebookSectionCourseAffinity(SourceObjectMixin):
    """
    Source: gradebook.gradebook_section_course_aff
    """
    source_object_table = 'gradebook_section_course_aff'
    source_object_schema = 'gradebook'

    gradebook = models.ForeignKey(Gradebook)
    section = models.ForeignKey(Section)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(Staff)
    created = models.DateTimeField()
    modified = models.DateTimeField()


class OverallScoreCache(SourceObjectMixin):
    """
    Source: gradebook.overall_score_cache

    * This is our go-to for gradebook scores
    """
    source_object_table = 'overall_score_cache'
    source_object_schema = 'gradebook'

    student = models.ForeignKey(Student)
    gradebook = models.ForeignKey(Gradebook)
    possible_points = models.FloatField(null=True)
    points_earned = models.FloatField(null=True)
    percentage = models.FloatField(null=True)
    mark = models.CharField(max_length=255, null=True)
    missing_count = models.IntegerField(null=True)
    zero_count = models.IntegerField(null=True)
    excused_count = models.IntegerField(null=True)


class CategoryScoreCache(SourceObjectMixin):
    """
    Source: gradebook.category_score_cache
    """
    source_object_table = 'category_score_cache'
    source_object_schema = 'gradebook'

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
