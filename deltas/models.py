from django.db import models
from django.utils import timezone

from clarify.models import Student, Assignment, Category, Score, UserProfile, \
    Gradebook, Score
from sis_mirror.models import Gradebooks

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

    # category average fields
    score = models.ForeignKey(Score, null=True)
    context_record = models.ForeignKey(CategoryGradeContextRecord, null=True)
    category_average_before = models.FloatField(null=True)
    category_average_after = models.FloatField(null=True)

    # missing assignment and category
    gradebook = models.ForeignKey(Gradebook, null=True)

    # attendance field
    settled = models.BooleanField(default=False)

    def __str__(self):
        out_string = f"{self.student.id}: {self.type}"
        if self.type == self.CATEGORY:
            out_string += f" | S_ID:{self.score_id}, " \
                          f"CR_ID: {self.context_record.id}, " \
                          f"CAB:{str(self.category_average_before)[:4]}, " \
                          f"CAA:{str(self.category_average_after)[:4]}"
        if self.type == self.CATEGORY or self.type == self.MISSING:
            out_string += f" | GB_ID:{self.gradebook_id}"

        return out_string

    @classmethod
    def return_response_query(cls, profile_id, student_id=None, delta_type=None):
        gradebook_ids = Gradebook\
            .get_all_current_gradebook_ids_for_user_profile(profile_id)

        filters = {
            'gradebook_id__in': gradebook_ids
        }

        if delta_type and delta_type in ['missing', 'category']:
            filters = {'type': delta_type}

        if student_id:
            filters = {'student_id': student_id}

        sections_for_profile = "__".join([
            "student",
            "enrollmentrecord",
            "section",
            "staffsectionrecord",
            "user_profile_id"
        ])

        queryset = (
            cls.objects
                .filter(**{sections_for_profile: profile_id})
                .order_by('student_id', '-id')
        )

        prefetch_list = ['gradebook']

        if delta_type == "missing" or not delta_type:
            prefetch_list += [
                "missingassignmentrecord_set",
                "missingassignmentrecord_set__assignment"
            ]

        if delta_type == "category" or not delta_type:
            prefetch_list += [
                "score__assignment",
                "context_record",
                "context_record__category"
            ]

        return (queryset
                    .filter(**filters)
                    .prefetch_related(*prefetch_list)
                    .distinct()
                    .all())


class MissingAssignmentRecord(models.Model):
    delta = models.ForeignKey(Delta)
    assignment = models.ForeignKey(Assignment)
    missing_on = models.DateField()


class Action(models.Model):
    TYPE_CHOICES = (
        ('note', 'Note'),
        ('call', 'Call'),
        ('message', 'Message'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=255, default=TYPE_CHOICES[0][0])
    created_by = models.ForeignKey(UserProfile)
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
