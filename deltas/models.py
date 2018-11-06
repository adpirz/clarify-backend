from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from sis_pull.models import Student, Assignment, Category, Score, Staff, \
    Gradebook, ScoreCache

"""
Allows for easy lookup of scores by date
"""


class Date(models.Transform):
    lookup_name = 'date'
    function = 'DATE'


models.DateTimeField.register_lookup(Date)


class CategoryGradeContextRecord(models.Model):
    category = models.ForeignKey(Category)
    date = models.DateField()

    total_points_possible = models.FloatField()
    average_points_earned = models.FloatField()

    class Meta:
        unique_together = ('category', 'date')


class Delta(models.Model):
    MISSING = 'missing'
    CATEGORY = 'category'
    ATTENDANCE = 'attendance'

    DELTA_TYPE_CHOICES = [
        (MISSING, 'Missing Assignments delta'),
        (CATEGORY, 'Category delta'),
        (ATTENDANCE, 'Attendance delta'),
    ]

    # meta fields
    type = models.CharField(choices=DELTA_TYPE_CHOICES,
                            max_length=255, blank=False)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(Student)

    # missing assignment fields
    missing_assignments = models.ManyToManyField(
        Assignment, through='MissingAssignmentRecord')
    gradebook = models.ForeignKey(Gradebook, null=True)

    # category average fields
    score = models.ForeignKey(ScoreCache, null=True)
    context_record = models.ForeignKey(CategoryGradeContextRecord, null=True)
    category_average_before = models.FloatField(null=True)
    category_average_after = models.FloatField(null=True)

    # attendance field
    attendance_dates = JSONField(null=True)
    settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.id}: {self.type}"

    def response_shape(self):
        response = {
            "student_id": self.student_id,
            "created_on": self.created_on,
            "updated_on": self.updated_on,
            "type": self.type
        }

        if self.type == "missing":
            response["missing_assignments"] = [
                a.response_shape() for a in
                self.missingassignmentrecord_set.all()
            ]
            response["gradebook_id"] = self.gradebook_id
            response["gradebook_name"] = self.gradebook.gradebook_name

        return response


class MissingAssignmentRecord(models.Model):
    delta = models.ForeignKey(Delta)
    assignment = models.ForeignKey(Assignment)
    missing_on = models.DateField()

    def response_shape(self):
        return {
            "assignment_name": self.assignment.short_name,
            "assignment_id": self.assignment_id,
            "due_date": self.assignment.due_date,
            "missing_on": self.missing_on
        }


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
