# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

"""
Order of loading:
    - Students
    - Users
    - Sites
    - AFs
    - Sections
    - Categories
    - Courses
    - Gradebooks
    - DailyRecords
    - GradeLevels
    - GradebookSectionCourseAff
    - OSC
    - SS_CUBE
    - Csc

"""
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    middle_name = models.CharField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    creation_time = models.DateTimeField(blank=True, null=True)
    field_last_mod_time = models.DateTimeField(db_column='_last_mod_time', blank=True, null=True)  # Field renamed because it started with '_'.
    last_name = models.CharField(max_length=255, blank=True, null=True)
    local_student_id = models.CharField(max_length=30)
    name_suffix = models.CharField(max_length=10, blank=True, null=True)
    aka_first_name = models.CharField(max_length=200, blank=True, null=True)
    aka_last_name = models.CharField(max_length=200, blank=True, null=True)
    aka_middle_name = models.CharField(max_length=200, blank=True, null=True)
    aka_name_suffix = models.CharField(max_length=200, blank=True, null=True)
    state_student_id = models.CharField(max_length=30, blank=True, null=True)
    migrant_ed_student_id = models.CharField(max_length=30, blank=True, null=True)
    birth_city = models.CharField(max_length=100, blank=True, null=True)
    birth_state = models.IntegerField(blank=True, null=True)
    birth_country = models.IntegerField(blank=True, null=True)
    three_years_us_schooling = models.NullBooleanField()
    interdistrict_transfer = models.NullBooleanField()
    field_residence_district = models.CharField(db_column='_residence_district', max_length=200, blank=True, null=True)  # Field renamed because it started with '_'.
    field_gate = models.NullBooleanField(db_column='_gate')  # Field renamed because it started with '_'.
    field_nslp = models.NullBooleanField(db_column='_nslp')  # Field renamed because it started with '_'.
    birthdate_verification = models.IntegerField(blank=True, null=True)
    homeless_dwelling_type = models.IntegerField(blank=True, null=True)
    english_proficiency = models.IntegerField(blank=True, null=True)
    primary_ethnicity = models.IntegerField(blank=True, null=True)
    primary_language = models.IntegerField(blank=True, null=True)
    correspondence_language = models.IntegerField(blank=True, null=True)
    residential_status = models.IntegerField(blank=True, null=True)
    special_needs_status = models.IntegerField(blank=True, null=True)
    district_enter_date = models.DateField(blank=True, null=True)
    field_has_504_plan = models.NullBooleanField(db_column='_has_504_plan')  # Field renamed because it started with '_'.
    home_address_is_mailing_address = models.BooleanField()
    gender = models.CharField(max_length=1, blank=True, null=True)
    number_504accommodations = models.TextField(db_column='504accommodations', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_504annual_review_date = models.DateField(db_column='504annual_review_date', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    photo_release = models.NullBooleanField()
    military_recruitment = models.NullBooleanField()
    field_exit_date = models.DateField(db_column='_exit_date', blank=True, null=True)  # Field renamed because it started with '_'.
    bus_num = models.CharField(max_length=100, blank=True, null=True)
    pickup_time = models.TimeField(blank=True, null=True)
    last_school_year = models.IntegerField(blank=True, null=True)
    lunch_id = models.CharField(max_length=30, blank=True, null=True)
    school_enter_date = models.DateField(blank=True, null=True)
    local_lunch_id = models.CharField(max_length=40, blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)
    social_security_number = models.CharField(max_length=9, blank=True, null=True)
    bus_depart_time = models.TimeField(blank=True, null=True)
    bus_depart_num = models.CharField(max_length=100, blank=True, null=True)
    prior_district = models.CharField(max_length=255, blank=True, null=True)
    prior_school = models.CharField(max_length=255, blank=True, null=True)
    sst_date = models.DateField(blank=True, null=True)
    avid_grade_level_id = models.IntegerField(blank=True, null=True)
    avid_enter_date = models.DateField(blank=True, null=True)
    avid_exit_date = models.DateField(blank=True, null=True)
    field_migrant = models.NullBooleanField(db_column='_migrant')  # Field renamed because it started with '_'.
    graduation_requirement_year = models.IntegerField(blank=True, null=True)
    hsee_ela_status = models.CharField(max_length=10, blank=True, null=True)
    hsee_math_status = models.CharField(max_length=10, blank=True, null=True)
    us_abroad = models.NullBooleanField()
    military_family = models.NullBooleanField()
    military_leave_date = models.DateField(blank=True, null=True)
    entered_grade_level_id = models.IntegerField(blank=True, null=True)
    passed_hsee_ela = models.NullBooleanField()
    hsee_math_score = models.IntegerField(blank=True, null=True)
    hsee_math_date = models.DateField(blank=True, null=True)
    passed_hsee_math = models.NullBooleanField()
    hsee_ela_score = models.IntegerField(blank=True, null=True)
    hsee_ela_date = models.DateField(blank=True, null=True)
    internet_release = models.NullBooleanField()
    graduation_status = models.IntegerField(blank=True, null=True)
    next_school_site_id = models.IntegerField(blank=True, null=True)
    previous_id = models.CharField(max_length=30, blank=True, null=True)
    home_address_verification_date = models.DateField(blank=True, null=True)
    service_learning_hours = models.FloatField(blank=True, null=True)
    ag_satisfied = models.NullBooleanField()
    is_hispanic = models.NullBooleanField()
    parent_education_level = models.IntegerField(blank=True, null=True)
    cumulative_file_sent_to = models.CharField(max_length=255, blank=True, null=True)
    cumulative_file_sent_on = models.DateField(blank=True, null=True)
    is_homeless = models.NullBooleanField()
    expected_receiver_school = models.IntegerField(blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    field_english_proficiency_date = models.DateField(db_column='_english_proficiency_date', blank=True, null=True)  # Field renamed because it started with '_'.
    cumulative_file_recvd_from = models.CharField(max_length=255, blank=True, null=True)
    cumulative_file_recvd_on = models.DateField(blank=True, null=True)
    child_care = models.NullBooleanField()
    is_f1_visa = models.NullBooleanField()
    is_foster_care = models.NullBooleanField()
    username = models.CharField(max_length=100, blank=True, null=True)
    birth_order = models.IntegerField(blank=True, null=True)
    mothers_maiden_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    resident_county_id = models.IntegerField(blank=True, null=True)
    mentor_name = models.CharField(max_length=255, blank=True, null=True)
    expected_graduation_year = models.IntegerField(blank=True, null=True)
    hazard_id = models.IntegerField(blank=True, null=True)
    lunch_balance = models.FloatField(blank=True, null=True)
    import_student_id = models.CharField(max_length=30)
    info_sharing_opt_out = models.NullBooleanField()
    case_manager_504 = models.CharField(max_length=255, blank=True, null=True)
    pre_k_funding_source = models.IntegerField(blank=True, null=True)
    prior_to_k_experience = models.IntegerField(blank=True, null=True)
    pre_k_length = models.CharField(max_length=255, blank=True, null=True)
    foster_care_id = models.CharField(max_length=100, blank=True, null=True)
    student_guid = models.UUIDField()
    reported_first_name = models.CharField(max_length=100, blank=True, null=True)
    reported_last_name = models.CharField(max_length=100, blank=True, null=True)
    reported_middle_name = models.CharField(max_length=100, blank=True, null=True)
    reported_gender = models.CharField(max_length=1, blank=True, null=True)
    military_family_indicator = models.IntegerField()
    cellphone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.last_name + ", " + self.first_name

    class Meta:
        managed = False
        db_table = 'students'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    suffix = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=20, blank=True, null=True)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    zip = models.CharField(max_length=11, blank=True, null=True)
    last_mod_by = models.IntegerField(blank=True, null=True)
    email1 = models.CharField(max_length=255, blank=True, null=True)
    email2 = models.CharField(max_length=255, blank=True, null=True)
    credentials = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    sign_attendance = models.NullBooleanField()
    job_title = models.CharField(max_length=200, blank=True, null=True)
    staff_education_level = models.IntegerField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    exit_date = models.DateField(blank=True, null=True)
    name_former_first = models.CharField(max_length=200, blank=True, null=True)
    name_former_middle = models.CharField(max_length=200, blank=True, null=True)
    name_former_last = models.CharField(max_length=200, blank=True, null=True)
    primary_ethnicity = models.IntegerField(blank=True, null=True)
    allow_rollover = models.NullBooleanField()
    state_id = models.CharField(max_length=30, blank=True, null=True)
    is_god = models.NullBooleanField()
    is_hispanic = models.NullBooleanField()
    ssn4 = models.CharField(max_length=4, blank=True, null=True)
    active = models.NullBooleanField()
    local_user_id = models.CharField(max_length=50, blank=True, null=True)
    local_user_concat_id = models.CharField(max_length=50, blank=True, null=True)
    password_expiration_date = models.DateField(blank=True, null=True)
    field_last_login_time = models.DateTimeField(db_column='_last_login_time', blank=True, null=True)  # Field renamed because it started with '_'.
    bypass_remote_auth = models.BooleanField()
    exclude_from_state_reporting = models.NullBooleanField()
    field_recent_login_count = models.IntegerField(db_column='_recent_login_count')  # Field renamed because it started with '_'.
    creation_time = models.DateTimeField(blank=True, null=True)
    last_mod_time = models.DateTimeField(blank=True, null=True)
    badge_access_key = models.CharField(max_length=255, blank=True, null=True)
    password_version = models.IntegerField()
    user_guid = models.UUIDField()
    illuminate_employee = models.BooleanField()

    def __str__(self):
        return self.username

    class Meta:
        managed = False
        db_table = 'users'


class Sites(models.Model):
    site_id = models.IntegerField(primary_key=True)
    site_name = models.CharField(max_length=255)
    site_type_id = models.IntegerField()
    start_grade_level_id = models.IntegerField(blank=True, null=True)
    end_grade_level_id = models.IntegerField(blank=True, null=True)
    parent_site_id = models.IntegerField()
    attendance_lock = models.BooleanField()
    address = models.CharField(max_length=255, blank=True, null=True)
    phone1 = models.CharField(max_length=100, blank=True, null=True)
    phone2 = models.CharField(max_length=100, blank=True, null=True)
    principal_name = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    academy_type = models.CharField(max_length=10, blank=True, null=True)
    title1_math = models.NullBooleanField()
    title1_reading = models.NullBooleanField()
    opportunity_school = models.NullBooleanField()
    continuation_school = models.NullBooleanField()
    has_students = models.NullBooleanField()
    fax = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.IntegerField()
    computers_for_instruction = models.IntegerField(blank=True, null=True)
    classrooms_with_internet = models.IntegerField(blank=True, null=True)
    calendar_type_id = models.IntegerField(blank=True, null=True)
    state_school_id = models.CharField(max_length=255, blank=True, null=True)
    num_weeks = models.FloatField(blank=True, null=True)
    num_hours = models.FloatField(blank=True, null=True)
    middle_transcript_grade_level_ids = models.TextField(blank=True, null=True)  # This field type is a guess.
    high_transcript_grade_level_ids = models.TextField(blank=True, null=True)  # This field type is a guess.
    lt = models.IntegerField(blank=True, null=True)
    rt = models.IntegerField(blank=True, null=True)
    truancy_letter_contact_name = models.CharField(max_length=255, blank=True, null=True)
    truancy_letter_contact_title = models.CharField(max_length=255, blank=True, null=True)
    site_long_name = models.CharField(max_length=255, blank=True, null=True)
    track_attendance = models.BooleanField()
    asam_school = models.NullBooleanField()
    ceeb_code = models.CharField(max_length=10, blank=True, null=True)
    exclude_from_state_reporting = models.NullBooleanField()
    local_site_id = models.CharField(max_length=25, blank=True, null=True)
    exclude_from_current_sites = models.NullBooleanField()
    non_public_school = models.NullBooleanField()
    did_not_meet_ayp_three_consecutive_years = models.NullBooleanField()
    msds_s2e2_code = models.CharField(max_length=5, blank=True, null=True)
    county_id = models.IntegerField(blank=True, null=True)
    state_district_id = models.CharField(max_length=20, blank=True, null=True)
    skill_center = models.NullBooleanField()
    geolocation = models.CharField(max_length=32, blank=True, null=True)
    site_guid = models.UUIDField()
    site_url = models.CharField(max_length=255, blank=True, null=True)
    is_disabled = models.BooleanField()
    nces_id = models.CharField(max_length=255, blank=True, null=True)
    is_special_ed_school = models.NullBooleanField()
    is_magnet_school = models.NullBooleanField()
    magnet_full_participation = models.NullBooleanField()
    is_charter_school = models.NullBooleanField()
    is_alternative_school = models.NullBooleanField()
    alternative_focus = models.CharField(max_length=255, blank=True, null=True)
    is_ap_self_selection = models.NullBooleanField()
    show_report_cards = models.NullBooleanField()

    def __str__(self):
        return self.site_name

    class Meta:
        managed = False
        db_table = 'sites'


class AttendanceFlags(models.Model):
    attendance_flag_id = models.AutoField(primary_key=True)
    character_code = models.CharField(max_length=30)
    flag_text = models.CharField(max_length=255, blank=True, null=True)
    precedence = models.IntegerField()
    is_present = models.BooleanField()
    is_excused = models.BooleanField()
    display_code = models.CharField(max_length=100)
    is_reconciled = models.BooleanField()
    is_tardy = models.BooleanField()
    trigger_truancy = models.BooleanField()
    trigger_tardy = models.BooleanField()
    trigger_irregular = models.BooleanField()
    is_30min_tardy = models.BooleanField()
    system_key = models.CharField(max_length=255, blank=True, null=True)
    is_permissive = models.BooleanField()
    is_truancy = models.BooleanField()
    is_suspension = models.BooleanField()
    is_verified = models.BooleanField()
    attendance_flag_type_id = models.IntegerField()
    attendance_program_set_id = models.IntegerField(blank=True, null=True)
    is_apportioned = models.BooleanField()
    apportionment = models.DecimalField(max_digits=4, decimal_places=3)
    apportionment_secondary_flag_type_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'attendance_flags'


class Sections(models.Model):
    section_id = models.IntegerField(primary_key=True)
    seating_chart_rows = models.IntegerField(blank=True, null=True)
    seating_chart_cols = models.IntegerField(blank=True, null=True)
    room_id = models.IntegerField(blank=True, null=True)
    is_core = models.BooleanField()
    local_section_id = models.CharField(max_length=100, blank=True, null=True)
    section_name = models.CharField(max_length=255, blank=True, null=True)
    teaching_type = models.CharField(max_length=50, blank=True, null=True)
    multiple_teacher_status = models.CharField(max_length=10, blank=True, null=True)
    include_in_csr_reports = models.NullBooleanField()
    independent_study = models.BooleanField()
    distance_learning = models.BooleanField()
    is_attendance_enabled = models.BooleanField()
    house_id = models.IntegerField(blank=True, null=True)
    language_of_instruction_id = models.IntegerField(blank=True, null=True)
    education_service = models.IntegerField(blank=True, null=True)
    instructional_strategy = models.IntegerField(blank=True, null=True)
    exclude_from_state_reporting = models.NullBooleanField()
    field_attendance_program_set_id = models.IntegerField(db_column='_attendance_program_set_id', blank=True, null=True)  # Field renamed because it started with '_'.
    mentor_teacher = models.NullBooleanField()
    field_alternative_learning_experience = models.BooleanField(db_column='_alternative_learning_experience')  # Field renamed because it started with '_'.
    skill_center = models.BooleanField()
    minutes_per_week = models.IntegerField()
    alternative_learning_experience_program_id = models.IntegerField(blank=True, null=True)
    alternative_learning_experience_type_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.section_name or str(self.section_id)


    class Meta:
        managed = False
        db_table = 'sections'


class CategoryTypes(models.Model):
    category_type_id = models.IntegerField(primary_key=True)
    category_type_name = models.CharField(max_length=255)
    is_academic = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'category_types'


class Categories(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    gradebook_id = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    category_type_id = models.IntegerField(blank=True, null=True)
    session_id = models.IntegerField(blank=True, null=True)
    max_pct = models.FloatField(blank=True, null=True)
    drop_lowest_x_scores = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'categories'


class Courses(models.Model):
    course_id = models.IntegerField(primary_key=True)
    short_name = models.CharField(max_length=30)
    long_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    school_course_id = models.CharField(max_length=20, blank=True, null=True)
    non_existent = models.SmallIntegerField(blank=True, null=True)
    credits = models.FloatField(blank=True, null=True)
    has_variable_credits = models.BooleanField()
    variable_credits_low = models.FloatField(blank=True, null=True)
    variable_credits_high = models.FloatField(blank=True, null=True)
    max_credits = models.FloatField(blank=True, null=True)
    is_specialed = models.NullBooleanField()
    course_requirement_priority = models.SmallIntegerField(blank=True, null=True)
    site_id = models.IntegerField()
    is_weighted = models.NullBooleanField()
    cbeds_course_id_num = models.CharField(max_length=25, blank=True, null=True)
    eq_course_id = models.IntegerField(blank=True, null=True)
    level = models.FloatField(blank=True, null=True)
    is_non_academic = models.NullBooleanField()
    is_active = models.NullBooleanField()
    site_type_id = models.IntegerField(blank=True, null=True)
    department_id = models.IntegerField(blank=True, null=True)
    num_timeblocks = models.IntegerField()
    term_length = models.FloatField(blank=True, null=True)
    term_offered = models.FloatField(blank=True, null=True)
    max_capacity = models.IntegerField(blank=True, null=True)
    min_capacity = models.IntegerField(blank=True, null=True)
    average_capacity = models.IntegerField(blank=True, null=True)
    is_intervention = models.NullBooleanField()
    session_type_id = models.IntegerField(blank=True, null=True)
    start_academic_year = models.IntegerField(blank=True, null=True)
    end_academic_year = models.IntegerField(blank=True, null=True)
    term_covered = models.IntegerField(blank=True, null=True)
    field_nclb_core = models.CharField(db_column='_nclb_core', max_length=1, blank=True, null=True)  # Field renamed because it started with '_'.
    course_type = models.IntegerField(blank=True, null=True)
    nclb_instructional_level = models.IntegerField(blank=True, null=True)
    course_content = models.IntegerField(blank=True, null=True)
    non_standard_instructional_level = models.IntegerField(blank=True, null=True)
    education_service = models.IntegerField(blank=True, null=True)
    instructional_strategy = models.IntegerField(blank=True, null=True)
    program_funding_source = models.IntegerField(blank=True, null=True)
    cte_funding_provider = models.IntegerField(blank=True, null=True)
    tech_prep = models.BooleanField()
    language_of_instruction_id = models.IntegerField(blank=True, null=True)
    field_always_include_on_hs_transcript = models.NullBooleanField(db_column='_always_include_on_hs_transcript')  # Field renamed because it started with '_'.
    include_in_ada_reporting = models.BooleanField()
    attendance_program_set_id = models.IntegerField(blank=True, null=True)
    exclude_from_state_reporting = models.NullBooleanField()
    crdc_course_area_id = models.IntegerField(blank=True, null=True)
    crdc_is_ap = models.NullBooleanField()
    crdc_is_ib = models.NullBooleanField()
    transcript_inclusion = models.NullBooleanField()
    ap_ib_course_id = models.IntegerField(blank=True, null=True)
    cip_code_id = models.IntegerField(blank=True, null=True)
    state_course_name = models.CharField(max_length=100, blank=True, null=True)
    hide_ms_credits = models.BooleanField()
    scholarship_program_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.short_name or str(self.course_id)


    class Meta:
        managed = False
        db_table = 'courses'


class Gradebooks(models.Model):
    gradebook_id = models.IntegerField(primary_key=True)
    created_on = models.DateTimeField()
    created_by = models.ForeignKey(Users, db_column='created_by')
    show_inactive_students = models.BooleanField()
    auto_save_mins = models.IntegerField(blank=True, null=True)
    gradebook_name = models.CharField(max_length=255, blank=True, null=True)
    num_visible_assignments = models.IntegerField()
    lock_published_gp = models.BooleanField()
    parent_portal = models.BooleanField()
    active = models.BooleanField()
    version = models.IntegerField()
    academic_year = models.IntegerField()
    session_type_id = models.IntegerField()
    is_deleted = models.BooleanField()

    def __str__(self):
        return self.gradebook_name or str(self.gradebook_id)

    @classmethod
    def get_all_current_gradebooks_for_user_id(cls, user_id):
        # TODO: What about gradebooks that have transferred owners?
        return cls.objects.filter(
            active=True, created_by=user_id
        ).all()

    class Meta:
        managed = False
        db_table = 'gradebooks'


class DailyRecords(models.Model):
    attendance_flag = models.ForeignKey(AttendanceFlags,
                                        db_column='attendance_flag_id')
    student = models.ForeignKey(Students, primary_key=True)
    site = models.ForeignKey(Sites, primary_key=True)
    date = models.DateField(primary_key=True)

    @classmethod
    def pull_query(cls):
        return cls.objects.filter(date__gte='2017-08-01')

    class Meta:
        managed = False
        db_table = 'daily_records'


class GradeLevels(models.Model):
    grade_level_id = models.IntegerField(primary_key=True)
    sort_order = models.IntegerField()
    short_name = models.CharField(max_length=255, blank=True, null=True)
    long_name = models.CharField(max_length=255, blank=True, null=True)
    standard_age = models.SmallIntegerField(blank=True, null=True)
    state_id = models.CharField(max_length=455, blank=True, null=True)
    system_sort_order = models.IntegerField(blank=True, null=True)
    system_key = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.long_name

    class Meta:
        managed = False
        db_table = 'grade_levels'


class GradebookSectionCourseAff(models.Model):
    gsca_id = models.IntegerField(primary_key=True)
    gradebook = models.ForeignKey(Gradebooks)
    section = models.ForeignKey(Sections)
    course = models.ForeignKey(Courses)
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(Users)

    def __str__(self):
        return f"{self.gradebook} - {self.section} - {self.course}"

    class Meta:
        managed = False
        db_table = 'gradebook_section_course_aff'


class OverallScoreCache(models.Model):
    cache_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students)
    gradebook = models.ForeignKey(Gradebooks)
    possible_points = models.FloatField(blank=True, null=True)
    points_earned = models.FloatField(blank=True, null=True)
    percentage = models.FloatField(blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    missing_count = models.IntegerField(blank=True, null=True)
    assignment_count = models.IntegerField(blank=True, null=True)
    zero_count = models.IntegerField(blank=True, null=True)
    excused_count = models.IntegerField(blank=True, null=True)
    timeframe_start_date = models.DateField()
    timeframe_end_date = models.DateField()
    calculated_at = models.DateTimeField()

    @classmethod
    def pull_query(cls):
        return (cls.objects.filter(calculated_at__gte='2017-08-01')
                .exclude(possible_points__isnull=True)
                .order_by('gradebook_id', 'student_id', '-calculated_at')
                .distinct('gradebook_id', 'student_id'))

    def __str__(self):
        return f"{self.student} grades for {self.gradebook}'"

    class Meta:
        managed = False
        db_table = 'overall_score_cache'


class Rooms(models.Model):
    room_id = models.IntegerField(primary_key=True)
    room_number = models.CharField(max_length=20)
    name = models.CharField(max_length=255, blank=True, null=True)
    site_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'rooms'


class Schedules(models.Model):
    schedule_id = models.IntegerField(primary_key=True)
    created_by = models.IntegerField(blank=True, null=True)
    last_modified_by = models.IntegerField(blank=True, null=True)
    schedule_name = models.CharField(max_length=255, blank=True, null=True)
    last_mod_time = models.IntegerField(blank=True, null=True)
    creation_time = models.IntegerField(blank=True, null=True)
    session_id = models.IntegerField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.IntegerField(blank=True, null=True)
    is_locked = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'schedules'


class SessionTypes(models.Model):
    code_id = models.AutoField(primary_key=True)
    code_key = models.CharField(max_length=255)
    code_translation = models.CharField(max_length=255, blank=True, null=True)
    site = models.ForeignKey(Sites, blank=True, null=True)
    system_key = models.CharField(max_length=255, blank=True, null=True)
    system_key_sort = models.IntegerField(blank=True, null=True)
    state_id = models.CharField(max_length=255, blank=True, null=True)
    sort_order = models.IntegerField(blank=True, null=True)
    system_state_id = models.IntegerField(blank=True, null=True)
    system_key_translation = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session_types'


class Sessions(models.Model):
    session_id = models.AutoField(primary_key=True)
    academic_year = models.IntegerField()
    site = models.ForeignKey(Sites)
    session_type = models.ForeignKey(SessionTypes, blank=True, null=True)
    field_positive_attendance = models.BooleanField(db_column='_positive_attendance')  # Field renamed because it started with '_'.
    elementary_grade_levels = models.TextField()  # This field type is a guess.
    district_reports = models.BooleanField()
    attendance_program_set_id = models.IntegerField()
    schedule = models.ForeignKey(Schedules, blank=True, null=True)
    is_high_poverty = models.BooleanField()
    is_remote_and_necessary = models.BooleanField()
    exclude_from_p223 = models.BooleanField()
    is_open_doors_youth_reengagement_program_school = models.BooleanField()
    is_online_instruction = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'sessions'


class SectionCourseAff(models.Model):
    section_course_aff_id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField()
    course_id = models.IntegerField()
    max_capacity = models.SmallIntegerField(blank=True, null=True)
    min_capacity = models.SmallIntegerField(blank=True, null=True)
    average_capacity = models.SmallIntegerField(blank=True, null=True)
    attendance_program_set_id = models.IntegerField(blank=True, null=True)
    credit_hours = models.FloatField(blank=True, null=True)
    outer_site_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'section_course_aff'


class SectionStudentAff(models.Model):
    ssa_id = models.IntegerField(primary_key=True)
    section = models.ForeignKey(Sections, blank=True, null=True)
    student = models.ForeignKey(Students, blank=True, null=True)
    seat_row = models.IntegerField(blank=True, null=True)
    seat_col = models.IntegerField(blank=True, null=True)
    entry_date = models.DateField()
    leave_date = models.DateField(blank=True, null=True)
    course = models.ForeignKey(Courses)
    entry_code_id = models.IntegerField(blank=True, null=True)
    exit_code_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'section_student_aff'


class Assignments(models.Model):
    assignment_id = models.IntegerField(primary_key=True)
    short_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=255, blank=True, null=True)
    assign_date = models.DateField()
    due_date = models.DateField()
    possible_points = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Categories, blank=True, null=True)
    is_active = models.BooleanField()
    description = models.TextField(blank=True, null=True)
    field_grading_period_id = models.IntegerField(db_column='_grading_period_id', blank=True, null=True)  # Field renamed because it started with '_'.
    auto_score_type = models.IntegerField(blank=True, null=True)
    auto_score_id = models.IntegerField(blank=True, null=True)
    possible_score = models.FloatField(blank=True, null=True)
    gradebook = models.ForeignKey(Gradebooks, blank=True, null=True)
    last_modified_by = models.IntegerField(blank=True, null=True)
    is_extra_credit = models.BooleanField()
    tags = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assignments'


class AssignmentGscaAff(models.Model):
    aga_id = models.IntegerField(primary_key=True)
    assignment = models.ForeignKey(Assignments)
    gsca = models.ForeignKey(GradebookSectionCourseAff)

    class Meta:
        managed = False
        db_table = 'assignment_gsca_aff'


class Scores(models.Model):
    score_id = models.IntegerField(primary_key=True)
    field_ssa_id = models.IntegerField(db_column='_ssa_id', blank=True, null=True)  # Field renamed because it started with '_'.
    assignment = models.ForeignKey(Assignments)
    value = models.FloatField(blank=True, null=True)
    gradebook = models.ForeignKey(Gradebooks)
    is_excused = models.BooleanField()
    notes = models.TextField(blank=True, null=True)
    entry = models.CharField(max_length=255, blank=True, null=True)
    is_valid = models.BooleanField()
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    student = models.ForeignKey(Students)

    def __str__(self):
        return f"Student: {self.student_id}, " +\
               f"Gradebook: {self.gradebook_id}, " +\
               f"Assignment: {self.assignment_id}"

    class Meta:
        managed = False
        db_table = 'scores'


class ScoreCache(models.Model):
    cache_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students, blank=True, null=True)
    gradebook = models.ForeignKey(Gradebooks, blank=True, null=True)
    assignment = models.ForeignKey(Assignments, blank=True, null=True)
    category = models.ForeignKey(Categories, blank=True, null=True)
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
    gs_id = models.IntegerField(blank=True, null=True)
    eva_id = models.IntegerField(blank=True, null=True)

    @classmethod
    def pull_query(cls):
        return (cls.objects
                .filter(calculated_at__gte=timezone.datetime(2018, 3, 1))
                .order_by('student_id', 'assignment_id', '-calculated_at')
                .distinct('student_id', 'assignment_id')
                .all())

    class Meta:
        managed = False
        db_table = 'score_cache'


class SectionTeacherAff(models.Model):
    sta_id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField()
    user_id = models.IntegerField()
    primary_teacher = models.NullBooleanField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    classroom_role_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'section_teacher_aff'


class SsCube(models.Model):
    site = models.ForeignKey(Sites, primary_key=True)
    academic_year = models.IntegerField(blank=True, primary_key=True)
    grade_level = models.ForeignKey(GradeLevels, primary_key=True)
    user = models.ForeignKey(Users, primary_key=True)
    section = models.ForeignKey(Sections, primary_key=True)
    course = models.ForeignKey(Courses, primary_key=True)
    student = models.ForeignKey(Students, primary_key=True)
    entry_date = models.DateField(blank=True, primary_key=True)
    leave_date = models.DateField(blank=True, primary_key=True)
    is_primary_teacher = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'ss_cube'


class SsCurrent(models.Model):
    student = models.ForeignKey(Students, primary_key=True)
    site = models.ForeignKey(Sites, primary_key=True)
    grade_level = models.ForeignKey(GradeLevels, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ss_current'


class Roles(models.Model):
    role_id = models.IntegerField(primary_key=True)
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

    class Meta:
        managed = False
        db_table = 'roles'


class Terms(models.Model):
    term_id = models.AutoField(primary_key=True)
    term_name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    schedule = models.ForeignKey(Schedules,
                                          db_column='_schedule_id',
                                          blank=True, null=True)
    session = models.ForeignKey(Sessions)
    term_num = models.IntegerField()
    term_type = models.IntegerField()
    local_term_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'terms'


class UserTermRoleAff(models.Model):
    utra_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users)
    role = models.ForeignKey(Roles)
    term = models.ForeignKey(Terms)
    last_schedule_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_term_role_aff'


class Timeblocks(models.Model):
    timeblock_id = models.IntegerField(primary_key=True)
    timeblock_name = models.CharField(max_length=255, blank=True, null=True)
    order_num = models.IntegerField()
    session = models.ForeignKey(Sessions)
    is_homeroom = models.NullBooleanField()
    occurrence_order = models.SmallIntegerField()
    is_primary = models.BooleanField()
    short_name = models.CharField(max_length=20, blank=True, null=True)
    include_in_extracts = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'timeblocks'


class SectionTimeblockAff(models.Model):
    stba_id = models.IntegerField(primary_key=True)
    section = models.ForeignKey(Sections)
    timeblock = models.ForeignKey(Timeblocks)

    class Meta:
        managed = False
        db_table = 'section_timeblock_aff'


class CategoryScoreCache(models.Model):
    cache_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students)
    gradebook = models.ForeignKey(Gradebooks)
    category = models.ForeignKey(Categories, blank=True, null=True)
    possible_points = models.FloatField(blank=True, null=True)
    points_earned = models.FloatField(blank=True, null=True)
    percentage = models.FloatField(blank=True, null=True)
    category_name = models.CharField(max_length=255, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True)
    mark_color = models.CharField(max_length=7, blank=True, null=True)
    missing_count = models.IntegerField(blank=True, null=True)
    assignment_count = models.IntegerField(blank=True, null=True)
    zero_count = models.IntegerField(blank=True, null=True)
    excused_count = models.IntegerField(blank=True, null=True)
    calculated_at = models.DateTimeField()
    timeframe_start_date = models.DateField()
    timeframe_end_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'category_score_cache'

    @classmethod
    def pull_query(cls):
        return (cls.objects
                .filter(calculated_at__gte='2018-01-01')
                .exclude(possible_points__isnull=True)
                .order_by('category_id', 'student_id', '-calculated_at')
                .distinct('category_id', 'student_id')
                )


class Standards(models.Model):
    standard_id = models.IntegerField(primary_key=True)
    parent_standard_id = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    subject_id = models.IntegerField(blank=True, null=True)
    guid = models.CharField(max_length=255, blank=True, null=True)
    state_num = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    seq = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    placeholder = models.NullBooleanField()
    organizer = models.CharField(max_length=255, blank=True, null=True)
    linkable = models.NullBooleanField()
    stem = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lft = models.IntegerField(blank=True, null=True)
    rgt = models.IntegerField(blank=True, null=True)
    custom_code = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'standards'


class StandardsCache(models.Model):
    cache_id = models.AutoField(primary_key=True)
    gradebook = models.ForeignKey(Gradebooks)
    student = models.ForeignKey(Students)
    standard = models.ForeignKey(Standards)
    percentage = models.FloatField(blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True)
    points_earned = models.FloatField(blank=True, null=True)
    possible_points = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    missing_count = models.IntegerField(blank=True, null=True)
    assignment_count = models.IntegerField(blank=True, null=True)
    zero_count = models.IntegerField(blank=True, null=True)
    excused_count = models.IntegerField(blank=True, null=True)
    timeframe_start_date = models.DateField()
    timeframe_end_date = models.DateField()
    calculated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'standards_cache'


class States(models.Model):
    state_id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=6)

    name = models.CharField(max_length=255)
    sort_order = models.IntegerField(blank=True, null=True)
    country_code = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'states'


class Subjects(models.Model):
    subject_id = models.IntegerField(primary_key=True)
    document = models.CharField(max_length=225, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    guid = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    seq = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    hidden = models.NullBooleanField()
    locale = models.CharField(max_length=100, blank=True, null=True)
    is_custom = models.NullBooleanField()
    state = models.ForeignKey(States, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subjects'


class GradingPeriods(models.Model):
    grading_period_id = models.IntegerField(primary_key=True)
    grading_period_name = models.CharField(max_length=200)
    term = models.ForeignKey(Terms)
    grading_window_start_date = models.DateField(blank=True, null=True)
    grading_window_end_date = models.DateField(blank=True, null=True)
    grading_period_start_date = models.DateField(blank=True, null=True)
    grading_period_end_date = models.DateField(blank=True, null=True)
    grading_window_start_date_overwrite = models.DateField(blank=True, null=True)
    grading_window_end_date_overwrite = models.DateField(blank=True, null=True)
    is_end_of_term = models.BooleanField()
    is_k6_report_card = models.NullBooleanField()
    disable_gpa = models.BooleanField()
    grading_period_num = models.IntegerField(blank=True, null=True)
    term_type = models.IntegerField(blank=True, null=True)
    track_id = models.IntegerField(blank=True, null=True)
    report_card_snapshot_date = models.DateField(blank=True, null=True)

    @classmethod
    def get_all_current_grading_periods(cls, date=None, site_id=None):
        if not date:
            date = timezone.now().date()

        grading_periods = (cls.objects
                           .filter(grading_period_start_date__lte=date,
                                   grading_period_end_date__gte=date))
        if not site_id:
            return grading_periods.all()

        return grading_periods.filter(term__session__site_id=site_id).all()

    class Meta:
        managed = False
        db_table = 'grading_periods'


class SectionGradingPeriodAff(models.Model):
    sgpa_id = models.IntegerField(primary_key=True)
    section = models.ForeignKey(Sections)
    course = models.ForeignKey(Courses)
    grading_period = models.ForeignKey(GradingPeriods)
    is_published = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'section_grading_period_aff'