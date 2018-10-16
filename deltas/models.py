from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from sis_pull.models import Student, Assignment, Category, Score

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
    completed_on = models.DateTimeField(default=timezone.now)
    missing_assignments = models.ManyToManyField(Assignment, through='MissingAssignmentRecord')
    score = models.ForeignKey(Score)
    category_average_before = models.FloatField()
    category_average_after = models.FloatField()
    attendance_dates = JSONField()
    type = models.CharField(choices=DELTA_TYPE_CHOICES, max_length=255)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

class MissingAssignmentRecord(models.Model):
    delta = models.ForeignKey(Delta)
    assignment = models.ForeignKey(Assignment)
    new = models.BooleanField()


class Action(models.Model):
    ACTION_TYPE_CHOICES = (
        ('note', 'Note'),
    )
    completed_on = models.DateTimeField()
    due_on = models.DateTimeField()
    action_type = models.CharField(choices=ACTION_TYPE_CHOICES, max_length=255)
    student = models.ForeignKey(Student)
    deltas = models.ManyToManyField(Delta)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)
    settled = models.BooleanField()
    note = models.TextField(blank=True)
