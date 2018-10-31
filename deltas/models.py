from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from sis_pull.models import Student, Assignment, Category, Score, Staff

# Create your models here.


class Delta(models.Model):
    MISSING = 'missing'
    CATEGORY = 'category'
    ATTENDANCE = 'attendance'

    DELTA_TYPE_CHOICES = [
        (MISSING, 'Missing Assignments delta'),
        (CATEGORY, 'Category delta'),
        (ATTENDANCE, 'Attendance delta'),
    ]

    updated_on = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)
    missing_assignments = models.ManyToManyField(
        Assignment, through='MissingAssignmentRecord')
    score = models.ForeignKey(Score, null=True)
    category_average_before = models.FloatField(null=True)
    category_average_after = models.FloatField(null=True)
    attendance_dates = JSONField(null=True)
    type = models.CharField(choices=DELTA_TYPE_CHOICES,
                            max_length=255, blank=False)
    settled = models.BooleanField(default=False)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.id}: {self.type}"


class MissingAssignmentRecord(models.Model):
    delta = models.ForeignKey(Delta)
    assignment = models.ForeignKey(Assignment)
    new = models.BooleanField()


class Action(models.Model):
    TYPE_CHOICES = (
        ('note', 'Note'),
        ('call', 'Call'),
        ('message', 'Message'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=255, default=TYPE_CHOICES[0][0])
    created_by = models.ForeignKey(Staff)
    student = models.ForeignKey(Student)
    completed_on = models.DateTimeField(null=True, blank=True)
    due_on = models.DateTimeField(null=True, blank=True)
    deltas = models.ManyToManyField(Delta, blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.id}: {self.type}"
