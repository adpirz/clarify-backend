from django.db import models
from clarify_backend.settings.base import AUTH_USER_MODEL


class Ethnicity(models.Model):
    code_id = models.IntegerField()
    code_key = models.CharField(max_length=10)
    code_translation = models.CharField(max_length=255)


class Student(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    ethnicity = models.ForeignKey(Ethnicity)

    def __str__(self):
        return "{}: {}, {}".format(self.pk, self.last_name, self.first_name)


class AttendanceFlag(models.Model):
    flag_text = models.CharField(max=255)
    character_code = models.CharField(max=30)


class AttendanceDailyRecord(models.Model):

    date = models.DateField()
    student = models.ForeignKey(Student)
    attendance_flag = models.ForeignKey(AttendanceFlag)

    class Meta:

        unique_together = ('school_day', 'student')

    def __str__(self):
        return f"{self.school_day}: {self.student} - {self.code}"


class Staff(models.Model):

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
