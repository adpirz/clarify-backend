
from django.apps import apps
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from utils import camel_to_underscore, get_academic_year


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
        kwargs[source_field_name] = self.id

        model_name = self.roster_model_name or "SectionLevelRosterPerYear"
        roster_model = apps.get_model(
            model_name=model_name, app_label=self._meta.app_label
        )

        return roster_model.objects.filter(**kwargs)

    def get_current_student_ids(self, **kwargs):
        """
        Return a list of distinct student_ids
        from current year and kwargs
        """
        new_kwargs = dict(kwargs)
        new_kwargs.update({"academic_year": get_academic_year()})
        rows = self._get_student_roster_rows(**new_kwargs)
        return rows\
            .distinct('student_id')\
            .values_list('student_id', flat=True)


class SourceObjectMixin:
    """
    Should implement source_table;
    If schema not 'public', should implement source_schema
    """
    source_table = None
    source_schema = 'public'
    source_id_field = None
    is_view = False


class GradeLevel(GetCurrentStudentsMixin, SourceObjectMixin, models.Model):
    """
    Source: public.grade_levels
    """
    source_table = 'grade_levels'
    source_id_field = 'grade_level_id'

    sort_order = models.IntegerField()
    short_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=455, null=True)

    def __str__(self):
        return self.long_name or self.short_name

    @staticmethod
    def get_users_current_grade_levels(staff):
        return SectionLevelRosterPerYear.objects\
            .filter(academic_year=get_academic_year())\
            .filter(user=staff)\
            .distinct('grade_level_id')\
            .values_list('grade_level_id', flat=True)


class Site(GetCurrentStudentsMixin, SourceObjectMixin, models.Model):
    """
    Source: public.sites
    Source for site types: public.site_types
    """
    source_table = 'sites'
    source_id_field = 'site_id'

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
    address = models.CharField(max_length=255, null=True)
    phone1 = models.CharField(max_length=100, null=True)
    phone2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=100, null=True)
    zip = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.site_name

    def get_site_type_label(self):
        return self.SITE_TYPE_CHOICES[self.site_type_id][1]

    def __str__(self):
        return self.site_name or "School {}".format(self.pk)


class Student(SourceObjectMixin, models.Model):
    """
    Source: public.students
    """

    source_table = 'students'
    source_id_field = 'student_id'

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

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def last_first(self):
        return "{}, {}".format(self.last_name, self.first_name)

    def get_current_active_section_ids(self):
        """Returns sections student is currently enrolled in"""
        now = timezone.now()
        return SectionLevelRosterPerYear.objects\
            .filter(student_id=self.id)\
            .filter(entry_date__lte=now, leave_date__gte=now)\
            .distinct('section_id')\
            .values_list('section_id', flat=True)

    def get_active_section_gradebook_ids(self):
        """Returns current gradebooks for given student"""
        sections_list = self.get_current_active_section_ids()
        return GradebookSectionCourseAffinity.objects\
            .filter(section_id__in=sections_list)\
            .distinct('gradebook_id')\
            .values_list('gradebook_id', flat=True)

    def is_enrolled(self):
        return CurrentRoster.objects.filter(student_id=self.id).exists()
    

class CurrentRoster(SourceObjectMixin, models.Model):
    
    source_table = 'ss_current'
    source_schema = 'matviews'
    is_view = True
    
    student = models.ForeignKey(Student)
    site = models.ForeignKey(Site)
    grade_level = models.ForeignKey(GradeLevel, blank=True, null=True)


class AttendanceFlag(SourceObjectMixin, models.Model):
    
    source_table = 'attendance_flag'
    source_id_field = 'attendance_flag_id'
    
    character_code = models.CharField(max_length=30, blank=True)
    flag_text = models.CharField(max_length=255, blank=True, null=True)

    def column_shape(self):
        return {"column_code": self.id,
                "label": self.flag_text}

    @classmethod
    def get_flag_columns(cls):
        return [ f.column_shape() for f in cls.objects.all()]

    @classmethod
    def get_exclude_columns(cls):
        return [f.id for f in cls.objects.all()
                 if f.character_code in ['I', '-', '_', 'D', 'N', 'X', 'A']]


class AttendanceDailyRecord(SourceObjectMixin, models.Model):
    """
    Source: attendance.daily_records
    Source for attendance flags: public.attendance_flags
    """
    source_table = 'daily_records'
    source_schema = 'attendance'
    is_view = True

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
    def calculate_summaries_for_student_records(student_records, student_id):
        """
        Returns a summary dict with a tuple (val, percentage) for each
        flag_id
        :param QuerySet<AttendanceDailyRecord>
        :return: {student_id: int, flag_id: (value, percentage) ... }
        """

        flag_dict = {f: 0 for f in \
                     AttendanceFlag.objects.values_list('id',
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


class Staff(SourceObjectMixin, models.Model):
    """
    Source: public.users
    """
    source_table = 'users'

    PREFIX_CHOICES = (
        ('MR', 'Mr.'),
        ('MS', 'Ms.'),
        ('MRS', 'Mrs.')
    )

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    prefix = models.CharField(choices=PREFIX_CHOICES, max_length=3, default='MS')
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(self.get_prefix_display(),
                                 self.user.first_name,
                                 self.user.last_name)
    
    def get_current_site_id(self):
        now = timezone.now()
        return (UserTermRoleAffinity.objects
                .filter(term__start_date__lte=now, term__end_date__gte=now)
                .filter(user_id=self.id)
                .first()
                .term.session.site_id)
    
    def get_current_role_ids(self):
        now = timezone.now()
        return (UserTermRoleAffinity.objects
                .filter(term__start_date__lte=now, term__end_date__gte=now)
                .filter(user_id=self.id)
                .values_list('role_id', flat=True)
                )
    
    def get_max_role_level(self):
        """ Above 700 is a site admin """
        max_level = 0
        role_ids = self.get_current_role_ids()
        if len(role_ids) == 1:
            return Role.objects.get(pk=role_ids[0]).role_level
        for rid in role_ids:
            level = Role.objects.get(pk=rid).role_level
            max_level = level if level > max_level else max_level
        
        return max_level

    class Meta:
        verbose_name = 'staff'
        verbose_name_plural = verbose_name


class Course(SourceObjectMixin, models.Model):
    """
    Source: public.courses
    """
    source_table = 'courses'
    source_id_field = 'course_id'

    short_name = models.CharField(max_length=30)
    long_name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    school_course_id = models.CharField(max_length=20, null=True)
    site = models.ForeignKey(Site)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.short_name or self.id

    @classmethod
    def get_current_course_ids(cls):
        """Returns a list of currently taught course source_ids"""
        return SectionLevelRosterPerYear.objects\
                .filter(academic_year=get_academic_year())\
                .distinct('course_id')\
                .values_list('course_id', flat=True)

    def get_current_section_ids(self):
        return SectionLevelRosterPerYear.objects\
                .filter(academic_year=get_academic_year())\
                .filter(course_id=self.source_id)\
                .distinct('section_id')\
                .values_list('section_id', flat=True)
    @classmethod
    def get_current_courses_for_user(cls, staff):
        return SectionLevelRosterPerYear.objects\
                .filter(academic_year=get_academic_year())\
                .filter(user=staff)\
                .distinct('course_id')\
                .values_list('course_id', flat=True)


class Section(GetCurrentStudentsMixin, SourceObjectMixin, models.Model):
    """
    Source: public.sections
    """
    source_table = 'sections'
    source_id_field = 'section_id'

    section_name = models.CharField(max_length=255, null=True)

    def __str__(self):
        if self.section_name and self.section_name != "":
            return self.section_name
        timeblock_name = SectionTimeblockAffinity.objects\
            .filter(section_id=self.id)\
            .order_by('-id')\
            .first()\
            .timeblock.timeblock_name

        course_name = SectionLevelRosterPerYear.objects\
            .filter(section_id=self.id)\
            .order_by('-entry_date')\
            .first()\
            .course.long_name

        return f"{timeblock_name} {course_name}"

    def get_course_id(self):
        gsca = GradebookSectionCourseAffinity.objects.filter(
            section_id=self.id).first()

        if gsca:
            return gsca.course_id
        else:
            return None
        
    def get_course(self):
        try:
            return Course.objects.get(pk=self.get_course_id())
        except Course.DoesNotExist:
            return None
    
    def get_timeblock(self):
        return (SectionTimeblockAffinity.objects
                .order_by('-id')
                .filter(section_id=self.id)
                .first().timeblock)


class SectionLevelRosterPerYear(SourceObjectMixin, models.Model):
    """
    Source: matviews.ss_cube
    * Key through-table to everything
    """
    source_table = 'ss_cube'
    source_schema = 'matviews'
    is_view = True

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


class Gradebook(SourceObjectMixin, models.Model):
    """
    Source: gradebook.gradebooks
    """
    source_table = 'gradebooks'
    source_schema = 'gradebook'
    source_id_field = 'gradebook_id'

    created_on = models.DateTimeField()
    created_by = models.ForeignKey(Staff)
    gradebook_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    academic_year = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.gradebook_name


class Category(SourceObjectMixin, models.Model):
    """
    Source: gradebook.categories
    """
    source_table = 'categories'
    source_schema = 'gradebook'
    source_id_field = 'category_id'

    category_name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    gradebook = models.ForeignKey(Gradebook)
    weight = models.FloatField(null=True)
    
    def __str__(self):
        return self.category_name or self.id


class GradebookSectionCourseAffinity(SourceObjectMixin, models.Model):
    """
    Source: gradebook.gradebook_section_course_aff
    """
    source_table = 'gradebook_section_course_aff'
    source_schema = 'gradebook'
    source_id_field = 'gsca_id'

    gradebook = models.ForeignKey(Gradebook)
    section = models.ForeignKey(Section)
    course = models.ForeignKey(Course)
    user = models.ForeignKey(Staff)
    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.gradebook} - {self.section} - {self.course}"


class OverallScoreCache(SourceObjectMixin, models.Model):
    """
    Source: gradebook.overall_score_cache

    * This is our go-to for gradebook scores
    """
    source_table = 'overall_score_cache'
    source_schema = 'gradebook'
    is_view = True

    student = models.ForeignKey(Student)
    gradebook = models.ForeignKey(Gradebook)
    possible_points = models.FloatField(null=True)
    points_earned = models.FloatField(null=True)
    percentage = models.FloatField(null=True)
    mark = models.CharField(max_length=255, null=True)
    missing_count = models.IntegerField(null=True)
    zero_count = models.IntegerField(null=True)
    excused_count = models.IntegerField(null=True)
    calculated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.student} grades for {self.gradebook}'"

    @classmethod
    def get_latest_for_student_and_gradebook(cls, student_id, gradebook_id):
        """Returns the latest row calculated for a given and student."""
        return cls.objects.exclude(possible_points__isnull=True)\
                    .filter(student_id=student_id, gradebook_id=gradebook_id)\
                    .order_by('-calculated_at')\
                    .first()

    @staticmethod
    def get_columns():

        return [{"column_code": i, "label": x} for i, x in enumerate(
            ['mark', 'percentage', 'possible_points',
             'points_earned', 'calculated_at']
        )]


class CategoryScoreCache(SourceObjectMixin, models.Model):
    """
    Source: gradebook.category_score_cache
    """
    source_table = 'category_score_cache'
    source_schema = 'gradebook'
    is_view = True

    student = models.ForeignKey(Student, blank=True, null=True)
    gradebook = models.ForeignKey(Gradebook, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    possible_points = models.FloatField(blank=True, null=True)
    points_earned = models.FloatField(blank=True, null=True)
    percentage = models.FloatField(blank=True, null=True)
    category_name = models.CharField(max_length=255, blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True)
    assignment_count = models.IntegerField(blank=True, null=True)
    missing_count = models.IntegerField(blank=True, null=True)
    excused_count = models.IntegerField(blank=True, null=True)
    zero_count = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    calculated_at = models.DateTimeField(blank=True, null=True)
    timeframe_start_date = models.DateField(blank=True, null=True)
    timeframe_end_date = models.DateField(blank=True, null=True)


class Assignment(SourceObjectMixin, models.Model):
    
    source_table = 'assignments'
    source_schema = 'gradebook'
    source_id_field = 'assignment_id'
    
    short_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=255, blank=True, null=True)
    assign_date = models.DateField()
    due_date = models.DateField()
    possible_points = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    is_active = models.BooleanField()
    description = models.TextField(blank=True, null=True)
    possible_score = models.FloatField(blank=True, null=True)
    gradebook = models.ForeignKey(Gradebook, blank=True, null=True)
    last_modified_by = models.ForeignKey(Staff, blank=True, null=True)
    is_extra_credit = models.BooleanField()
    tags = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.short_name
    

class ScoreCache(SourceObjectMixin, models.Model):
    
    source_table = 'score_cache'
    source_schema = 'gradebook'
    is_view = True
    
    student = models.ForeignKey(Student, blank=True, null=True)
    gradebook = models.ForeignKey(Gradebook, blank=True, null=True)
    assignment = models.ForeignKey(Assignment, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    is_excused = models.NullBooleanField()
    is_missing = models.NullBooleanField()
    points = models.FloatField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    percentage = models.FloatField(blank=True, null=True)
    use_for_calc = models.NullBooleanField()
    use_for_aggregate = models.NullBooleanField()
    use_category_weights = models.NullBooleanField()
    last_updated = models.DateTimeField(blank=True, null=True)
    calculated_at = models.DateTimeField()
    

class Timeblock(SourceObjectMixin, models.Model):

    source_table = 'timeblocks'
    source_id_field = 'timeblock_id'

    timeblock_name = models.CharField(max_length=255, blank=True, null=True)
    order_num = models.IntegerField()
    is_homeroom = models.NullBooleanField()
    occurrence_order = models.SmallIntegerField()
    is_primary = models.BooleanField()
    short_name = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.timeblock_name or self.short_name


class SectionTimeblockAffinity(SourceObjectMixin, models.Model):

    source_table = 'section_timeblock_aff'
    source_id_field = 'stba_id'

    section = models.ForeignKey(Section)
    timeblock = models.ForeignKey(Timeblock)


class SessionType(SourceObjectMixin, models.Model):
    
    source_table = 'session_types'
    source_schema = 'session_types'
    source_id_field = 'code_id'
    
    code_key = models.CharField(max_length=255)
    code_translation = models.CharField(max_length=255, blank=True, null=True)
    site = models.ForeignKey(Site, blank=True, null=True)
    system_key = models.CharField(max_length=255, blank=True, null=True)
    system_key_sort = models.IntegerField(blank=True, null=True)
    state_id = models.CharField(max_length=255, blank=True, null=True)
    sort_order = models.IntegerField(blank=True, null=True)
    system_state_id = models.IntegerField(blank=True, null=True)
    system_key_translation = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.code_translation


class Session(SourceObjectMixin, models.Model):
    
    source_table = 'sessions'
    source_id_field = 'session_id'
    
    academic_year = models.IntegerField()
    site = models.ForeignKey(Site)
    session_type = models.ForeignKey(SessionType, blank=True, null=True)
    
    def __str__(self):
        return f"{self.academic_year}: {self.site}: {self.session_type}"


class Role(SourceObjectMixin, models.Model):
    
    source_table = 'roles'
    source_id_field = 'role_id'
    
    role_name = models.CharField(max_length=255)
    role_level = models.IntegerField(blank=True, null=True)
    can_teach = models.BooleanField()
    can_counsel = models.BooleanField()
    job_classification_id = models.IntegerField(blank=True, null=True)
    role_short_name = models.CharField(max_length=255, blank=True, null=True)
    system_key = models.CharField(max_length=255, blank=True, null=True)
    system_key_sort = models.IntegerField(blank=True, null=True)
    can_refer_discipline = models.BooleanField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.role_name


class Term(SourceObjectMixin, models.Model):
    
    source_table = 'terms'
    source_id_field = 'term_id'
    
    term_name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    session = models.ForeignKey(Session)
    term_num = models.IntegerField()
    term_type = models.IntegerField()
    local_term_id = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.term_name


class UserTermRoleAffinity(SourceObjectMixin, models.Model):
    
    source_table = 'user_term_role_aff'
    source_id_field = 'utra_id'
    
    user = models.ForeignKey(Staff)
    role = models.ForeignKey(Role)
    term = models.ForeignKey(Term)
