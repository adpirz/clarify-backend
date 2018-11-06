from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from sis_mirror.models import Gradebooks
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

    def response_shape(self):
        return {
            "category_id": self.category_id,
            "category_name": self.category.category_name,
            "date": self.date,
            "total_points_possible": self.total_points_possible,
            "average_points_earned": self.average_points_earned
        }


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

    # category average fields
    score = models.ForeignKey(ScoreCache, null=True)
    context_record = models.ForeignKey(CategoryGradeContextRecord, null=True)
    category_average_before = models.FloatField(null=True)
    category_average_after = models.FloatField(null=True)

    # missing assignment and category
    gradebook = models.ForeignKey(Gradebook, null=True)

    # attendance field
    attendance_dates = JSONField(null=True)
    settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.id}: {self.type}"

    @classmethod
    def return_response_query(cls, staff_id, student_id=None, delta_type=None):
        gradebook_ids = Gradebook\
            .get_all_current_gradebook_ids_for_staff_id(staff_id)

        filters = {
            'gradebook_id__in': gradebook_ids
        }

        if delta_type and delta_type in ['missing', 'category']:
            filters = {'type': delta_type}

        if student_id:
            filters = {'student_id': student_id}

        queryset = cls.objects.filter(**filters)

        prefetch_list = ['gradebook']

        if delta_type == "missing" or not delta_type:
            prefetch_list += [
                "missingassignmentrecord_set",
                "missingassignmentrecord_set__assignment"
            ]

        if delta_type == "category" or not delta_type:
            prefetch_list += [
                "score__assignment",
                "context_record"
            ]

        return queryset.prefetch_related(*prefetch_list).all()

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
            response["sort_date"] = self.created_on

        if self.type == "category":
            response["last_assignment"] = self.score.assignment.short_name
            response["last_assignment_score"] = self.score.score
            response["last_assignment_points"] = self.score.points
            response["last_assignment_due_date"] = self.score.assignment.due_date
            response["score_last_updated"] = self.score.last_updated
            response["context_record"] = self.context_record.response_shape()
            response["category_average_before"] = self.category_average_before
            response["category_average_after"] = self.category_average_after
            response["sort_date"] = self.score.assignment.due_date

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
