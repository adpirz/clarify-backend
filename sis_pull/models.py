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

        return f"{self.date.strftime('%Y-%m-%d')}: " +\
               f"{self.student} - {self.attendance_flag}"


    @classmethod
    def get_records_for_student(cls, student_id,
                                from_date=None, to_date=None):
        """
        Get all relevant AttendanceDailyRecord instances for
        params.
        :return: QuerySet<AttendanceDailyRecord>
        """
        if to_date and not from_date:
            raise LookupError("Must have a from_date with a to_date")
        all_objects = cls.objects.filter(student_id=student_id)

        if from_date and to_date:
            return all_objects.filter(date__gte=from_date, date__lte=to_date)
        if from_date:
            return all_objects.filter(date__gte=from_date)

        return all_objects

    @classmethod
    def get_records_for_students(cls, student_ids,
                                 from_date=None, to_date=None):
        """
        Get all relevant AttendanceDailyRecords instances for a
        list of student_ids.
        :return: List[{student_id: int, records: QuerySet<ADR>}]
        """
        attendance_records_by_student = []

        for student_id in student_ids:
            student_records = dict({"student_id": student_id})
            student_records["records"] = cls.get_records_for_student(
                student_id, from_date=from_date, to_date=to_date
            )
            attendance_records_by_student.append(student_records)

        return attendance_records_by_student

    @staticmethod
    def calculate_summaries_for_student_records(student_records):
        """
        Returns a summary dict with a tuple (val, percentage) for each
        flag_id
        :param QuerySet<AttendanceDailyRecord>
        :return: {student_id: int, flag_id: (value, percentage) ... }
        """

        flag_dict = {f: 0 for f in \
                     AttendanceFlag.objects.values_list('id', flat=True)}

        summary_dict = dict()
        for record in student_records:
            if "student_id" not in summary_dict:
                summary_dict["student_id"] = record.student_id
            if record.student_id != summary_dict["student_id"]:
                raise AttributeError("Student records must all be same student.")
            flag_id = record.attendance_flag_id
            if flag_id not in flag_dict:
                flag_dict[flag_id] = 1
            else:
                flag_dict[flag_id] += 1

        for flag_id, value in flag_dict.items():
            summary_dict[flag_id] = (value, value/len(student_records))

        return summary_dict


    @classmethod
    def get_summaries_for_student(cls, student_id, from_date, to_date):
        """
        Returns a summary dict for a student with given date params.
        """
        return cls.calculate_summaries_for_student_records(
            cls.get_records_for_student(student_id,
                                        from_date=from_date, to_date=to_date)
        )

    @classmethod
    def get_summaries_for_students(cls, student_ids, from_date, to_date):
        """
        :return: List[{
            student_id: int, <flag_id>: (<val>, <percentage>)
        }]
        """
        summaries = []
        for student_id in student_ids:
            summaries.append(cls.get_summaries_for_student(
                student_id, from_date=from_date, to_date=to_date
            ))

        return summaries

    @classmethod
    def get_student_record_for_date(cls, student_id, date):
        """Get an individual date record for one student"""

        return cls.objects.get(student_id=student_id, date=date)

    @classmethod
    def get_student_records_for_date(cls, student_ids, date):
        """Get an individual date record for list of students"""

        return [cls.get_student_record_for_date(i, date)
                for i in student_ids]


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
