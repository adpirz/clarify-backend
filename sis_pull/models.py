from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from utils import camel_to_underscore, SourceObjectForeignKey, get_academic_year


class GetCurrentStudentsMixin(object):

    roster_model_name = None

    def _get_student_roster_rows(self, **extra):
        """
        Returns a QueryDict iterable filtered by model args
        :param extra: Extra filter args (e.g. site_id for GradeLevel, etc.)
        :return: QueryDict filtered on model args
        """
        source_field_name = camel_to_underscore(self.__class__.__name__) + '_id'
        kwargs = dict(extra)
        kwargs[source_field_name] = self.source_object_id

        model_name = self.roster_model_name or "SectionLevelRosterPerYear"
        roster_model = apps.get_model(
            model_name=model_name, app_label=self._meta.app_label
        )

        return roster_model.objects.filter(**kwargs)

    def get_current_student_ids(self, **kwargs):
        new_kwargs = dict(kwargs)
        new_kwargs.update({"academic_year": get_academic_year()})
        rows = self._get_student_roster_rows(**new_kwargs)
        return rows.values_list('student_id', flat=True)


class SourceObjectModel(models.Model):
    """
    Mixin to add source_object_id to a model
    Should implement source_object_table;
    If schema not 'public', should implement source_object_schema
    """
    source_object_id = models.PositiveIntegerField(null=True, unique=True)
    is_view = False

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


class GradeLevel(GetCurrentStudentsMixin, SourceObjectModel):
    """
    Source: public.grade_levels
    """
    source_object_table = 'grade_levels'

    sort_order = models.IntegerField()
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=455, null=True)

    def __str__(self):
        return long_name | short_name



class Site(GetCurrentStudentsMixin, SourceObjectModel):
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
    start_grade_level = SourceObjectForeignKey(GradeLevel,
                                          related_name='start_grade_level')
    end_grade_level = SourceObjectForeignKey(GradeLevel,
                                        related_name='end_grade_level')
    site_type_id = models.IntegerField(choices=SITE_TYPE_CHOICES)
    address = models.CharField(max_length=255, null=True)
    phone1 = models.CharField(max_length=100, null=True)
    phone2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=100, null=True)
    zip = models.CharField(max_length=10, null=True)

    def get_site_type_label(self):
        return self.SITE_TYPE_CHOICES[self.site_type_id][1]

    def __str__(self):
        return self.site_name | "School {}".format(self.pk)


class Student(SourceObjectModel):
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
        return "{} {}".format(self.first_name, self.last_name)


class AttendanceFlag(SourceObjectModel):
    source_object_table = "attendance_flag"

    character_code = models.CharField(max_length=30, blank=True)
    flag_text = models.CharField(max_length=255, blank=True, null=True)

    def column_shape(self):
        return {"column_code": self.source_object_id,
                "label": self.flag_text}

    @classmethod
    def get_flag_columns(cls):
        return [ f.column_shape() for f in cls.objects.all()]

    @classmethod
    def get_exclude_columns(cls):
        return [f.source_object_id for f in cls.objects.all()
                 if f.character_code in ['I', '-', '_', 'D', 'N', 'X', 'A']]


class AttendanceDailyRecord(SourceObjectModel):
    """
    Source: attendance.daily_records
    Source for attendance flags: public.attendance_flags
    """
    source_object_table = 'daily_records'
    source_object_schema = 'attendance'
    is_view = True

    date = models.DateField()
    site = SourceObjectForeignKey(Site)
    student = SourceObjectForeignKey(Student)
    attendance_flag = SourceObjectForeignKey(AttendanceFlag)

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
    def calculate_summaries_for_student_records(student_records, student_id):
        """
        Returns a summary dict with a tuple (val, percentage) for each
        flag_id
        :param QuerySet<AttendanceDailyRecord>
        :return: {student_id: int, flag_id: (value, percentage) ... }
        """

        flag_dict = {f: 0 for f in \
                     AttendanceFlag.objects.values_list('source_object_id',
                                                        flat=True)}

        def _row_shape(flag_id, value, total):
            percentage = 0 if value == 0 else value / total
            return {'column_code': flag_id,
                    'count': value,
                    'percentage': percentage}

        summary_dict = {"attendance_data": [], "student_id": student_id}

        for record in student_records:
            if record.student_id != summary_dict["student_id"]:
                raise AttributeError("Student records must all be same student.")
            flag_id = record.attendance_flag_id
            if flag_id not in flag_dict:
                flag_dict[flag_id] = 1
            else:
                flag_dict[flag_id] += 1

        for flag_id, value in flag_dict.items():
            total = len(student_records)
            summary_dict["attendance_data"].append(
                _row_shape(flag_id, value, total)
            )

        return summary_dict


    @classmethod
    def get_summaries_for_student(cls, student_id, from_date, to_date):
        """
        Returns a summary dict for a student with given date params.
        """
        return \
            cls.calculate_summaries_for_student_records(
                cls.get_records_for_student(student_id,
                                            from_date=from_date,
                                            to_date=to_date),
                student_id
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


class Staff(SourceObjectModel):
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


class Course(SourceObjectModel):
    """
    Source: public.courses
    """
    source_object_table = 'courses'

    short_name = models.CharField(max_length=30)
    long_name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    school_course_id = models.CharField(max_length=20, null=True)
    site = SourceObjectForeignKey(Site)
    is_active = models.BooleanField(default=True)


class Section(GetCurrentStudentsMixin, SourceObjectModel):
    """
    Source: public.sections
    """
    source_object_table = 'sections'

    section_name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.section_name


class SectionLevelRosterPerYear(SourceObjectModel):
    """
    Source: matviews.ss_cube
    * Key through-table to everything
    """
    source_object_table = 'ss_cube'
    source_object_schema = 'matviews'
    is_view = True

    site = SourceObjectForeignKey(Site)
    academic_year = models.PositiveIntegerField()
    grade_level = SourceObjectForeignKey(GradeLevel)
    user = SourceObjectForeignKey(Staff)
    section = SourceObjectForeignKey(Section)
    course = SourceObjectForeignKey(Course)
    student= SourceObjectForeignKey(Student)
    entry_date = models.DateField(null=True)
    leave_date = models.DateField(null=True)
    is_primary_teacher = models.NullBooleanField()


class Gradebook(SourceObjectModel):
    """
    Source: gradebook.gradebooks
    """
    source_object_table = 'gradebooks'
    source_object_schema = 'gradebook'

    created_on = models.DateTimeField()
    created_by = SourceObjectForeignKey(Staff)
    gradebook_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    academic_year = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)


class Category(SourceObjectModel):
    """
    Source: gradebook.categories
    """
    source_object_table = 'categories'
    source_object_schema = 'gradebook'

    category_name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    gradebook = SourceObjectForeignKey(Gradebook)
    weight = models.FloatField()


class GradebookSectionCourseAffinity(SourceObjectModel):
    """
    Source: gradebook.gradebook_section_course_aff
    """
    source_object_table = 'gradebook_section_course_aff'
    source_object_schema = 'gradebook'

    gradebook = SourceObjectForeignKey(Gradebook)
    section = SourceObjectForeignKey(Section)
    course = SourceObjectForeignKey(Course)
    user = SourceObjectForeignKey(Staff)
    created = models.DateTimeField()
    modified = models.DateTimeField()


class OverallScoreCache(SourceObjectModel):
    """
    Source: gradebook.overall_score_cache

    * This is our go-to for gradebook scores
    """
    source_object_table = 'overall_score_cache'
    source_object_schema = 'gradebook'
    is_view = True

    student = SourceObjectForeignKey(Student)
    gradebook = SourceObjectForeignKey(Gradebook)
    possible_points = models.FloatField(null=True)
    points_earned = models.FloatField(null=True)
    percentage = models.FloatField(null=True)
    mark = models.CharField(max_length=255, null=True)
    missing_count = models.IntegerField(null=True)
    zero_count = models.IntegerField(null=True)
    excused_count = models.IntegerField(null=True)


class CategoryScoreCache(SourceObjectModel):
    """
    Source: gradebook.category_score_cache
    """
    source_object_table = 'category_score_cache'
    source_object_schema = 'gradebook'
    is_view = True

    student = SourceObjectForeignKey(Student)
    gradebook = SourceObjectForeignKey(Gradebook)
    category = SourceObjectForeignKey(Category)
    possible_points = models.FloatField()
    points_earned = models.FloatField()
    percentage = models.FloatField()
    category_name = models.CharField(max_length=255)
    mark = models.CharField(max_length=255)
    assignment_count = models.IntegerField()
    calculated_at = models.DateTimeField()
    timeframe_start_date = models.DateField()
    timeframe_end_date = models.DateField()
