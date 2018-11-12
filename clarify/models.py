from django.contrib.auth.models import User
from django.db import models

# Create your models here.

"""

Abstract Base Models

"""


class CleverIDModel (models.Model):
    clever_id = models.CharField(max_length=50, blank=True)

    class Meta:
        abstract = True


class SISIDModel(models.Model):
    sis_id = models.IntegerField(null=True)

    class Meta:
        abstract = True


class NamedModel(CleverIDModel, SISIDModel):
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True


class PersonNameModel(SISIDModel, CleverIDModel):
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

    class Meta:
        abstract = True


class UserModel(SISIDModel, CleverIDModel):
    PREFIX_CHOICES = (
        ('MR', 'Mr.'),
        ('MS', 'Ms.'),
        ('MRS', 'Mrs.'),
    )

    name = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(User)
    prefix = models.CharField(max_length=3,
                              choices=PREFIX_CHOICES,
                              blank=True)

    def get_full_mame(self):
        if len(self.user.first_name) and len(self.user.last_name):
            return f"{self.user.first_name} {self.user.last_name}"
        if len(self.user.first_name):
            return self.user.first_name
        if len(self.user.last_name):
            return self.user.last_name
        if len(self.name):
            return self.name


"""

Concrete Models

"""


class Student(PersonNameModel):
    pass


class Staff(UserModel):
    pass


class Site(NamedModel):
    pass


class Term(NamedModel):
    academic_year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    site = models.ForeignKey(Site)


class GradeLevel(NamedModel):
    pass


class Section(NamedModel):
    course_name = models.CharField(max_length=255, blank=True)
    term = models.ForeignKey(Term)
    grade_level = models.ForeignKey(GradeLevel)


class EnrollmentRecord(models.Model):
    student = models.ForeignKey(Student)
    section = models.ForeignKey(Section)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)


class StaffSectionRecord(models.Model):
    staff = models.ForeignKey(Staff)
    section = models.ForeignKey(Section)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    primary_teacher = models.BooleanField(default=True)


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

    date = models.DateField
    student = models.ForeignKey(Student)
    flag = models.CharField(max_length=2, choices=FLAG_CHOICES)

    class Meta:
        unique_together = ('date', 'student')


class Gradebook(NamedModel):
    section = models.ForeignKey(Section)
    # Some gradebooks have multiple owners / viewers
    owners = models.ManyToManyField(Staff)


class Category(NamedModel):
    gradebook = models.ForeignKey(Gradebook)


class Assignment(NamedModel):
    # in case category doesn't exist, we keep
    # a gradebook record on the assignment
    gradebook = models.ForeignKey(Gradebook)
    category = models.ForeignKey(Category)

    # TODO: Which goes into final grade?
    possible_points = models.FloatField()
    possible_score = models.FloatField()


class Score(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)

    # Nullable if excused
    score = models.FloatField(null=True)
    value = models.FloatField(null=True)

    is_missing = models.BooleanField(default=False)
    is_excused = models.BooleanField(default=False)




