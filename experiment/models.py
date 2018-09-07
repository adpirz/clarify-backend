from django.db import models
from django.db.models import Sum, Max, Min
from django.utils import timezone

from sis_mirror.models import Scores


class AbstractScoreModel(models.Model):
    student_id = models.IntegerField()
    student_name = models.CharField(max_length=200, blank=True)
    mark = models.CharField(max_length=3, blank=True)
    percentage = models.FloatField(null=True)
    possible_points = models.FloatField(null=True)
    total_points = models.FloatField(null=True)
    number_of_assignments = models.IntegerField(default=0)
    number_of_missing_assignments = models.IntegerField(default=0)
    gradebook_id = models.IntegerField()
    gradebook_name = models.CharField(max_length=200)
    user_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        abstract = True


class StudentWeekCategoryScore(AbstractScoreModel):
    category_id = models.IntegerField()
    category_name = models.CharField(max_length=200)
    category_weight = models.FloatField()

    @staticmethod
    def _shape_category_grade_set(category_grades, start_date, end_date):
        out =  {
            'start_date': start_date,
            'end_date': end_date,
            'category_grades': category_grades.values(
                'student_id', 'percentage', 'possible_points', 'total_points',
                'number_of_assignments', 'gradebook_id', 'gradebook_name',
                'user_id', 'category_id', 'category_name', 'category_weight',
                'start_date', 'end_date'
            ),
            'gradebook_grades': category_grades.values(
                'student_id', 'gradebook_id', 'gradebook_name'
            ).annotate(
                total_possible_points=Sum('possible_points'),
                total_points_earned=Sum('total_points'),
                total_number_of_assignments=Sum('number_of_assignments'),
            )

        }

        return out


    @classmethod
    def get_all_scores_for_gradebook_in_timespan(
            cls, gradebook_id, start_date, end_date):

        def format_time(t):
            if isinstance(t, str):
                return timezone.datetime.strptime(t, '%Y-%m-%d')
            return t

        # Converge on date format for return dict,
        # ie. not a mix of strings and datetimes returned
        start_date = format_time(start_date)
        end_date = format_time(end_date)

        category_grades = cls.objects.filter(
            gradebook_id=gradebook_id,
            start_date=start_date,
            end_date=end_date
        )

        if not category_grades.exists():
            return None

        return cls._shape_category_grade_set(
            category_grades, start_date, end_date
        )

    @classmethod
    def get_all_scores_for_all_timespans(cls, gradebook_id):
        bookend_dates = (cls.objects
                         .filter(gradebook_id=gradebook_id)
                         .aggregate(Min('start_date'), Max('end_date'))
                         )

        start_date = bookend_dates.get('start_date__min')
        end_date = bookend_dates.get('end_date__max')

        category_grades = cls.objects.filter(
            gradebook_id=gradebook_id,
            start_date__gte=start_date,
            end_date__lte=end_date
        )

        return cls._shape_category_grade_set(
            category_grades, start_date, end_date
        )

    def next_score(self):
        return StudentWeekCategoryScore.objects.filter(
            gradebook_id=self.gradebook_id,
            student_id=self.student_id,
            start_date__gte=self.end_date
        ).order_by('start_date').first()

    def previous_score(self):
        return StudentWeekCategoryScore.objects.filter(
            gradebook_id=self.gradebook_id,
            student_id=self.student_id,
            end_date__lte=self.start_date
        ).order_by('-end_date').first()

    def d_previous(self):
        previous_score = self.previous_score()
        if not previous_score:
            return None
        return self.percentage - previous_score.percentage

    def get_all_assignments_for_score(self):
        return Scores.objects.filter(
            gradebook_id=self.gradebook_id,
            student_id=self.student_id,
            created__gte=self.start_date,
            created__lte=self.end_date,
        ).all()

    class Meta:
        unique_together = ('student_id',
                           'category_id',
                           'start_date',
                           'end_date')

    def __str__(self):
        return f"Student: {self.student_id}, " + \
               f"Gradebook: {self.gradebook_id}, " + \
               f"{self.start_date} to {self.end_date}"


class StudentWeekGradebookScore(AbstractScoreModel):
    class Meta:
        unique_together = ('student_id',
                           'gradebook_id',
                           'start_date',
                           'end_date')
