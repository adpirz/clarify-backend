from django.db import models
from django.db.models import Sum
from django.utils import timezone


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

        return {
            'start_date': start_date,
            'end_date': end_date,
            'category_grades': category_grades.values(
                'student_id', 'percentage', 'possible_points', 'total_points',
                'number_of_assignments', 'gradebook_id', 'gradebook_name',
                'user_id', 'category_id', 'category_name', 'category_weight'
            ),
            'gradebook_grades': category_grades.values(
                'student_id', 'gradebook_id', 'gradebook_name'
            ).annotate(
                total_possible_points=Sum('possible_points'),
                total_points_earned=Sum('total_points'),
                total_number_of_assignments=Sum('number_of_assignments'),
            )

        }

    @classmethod
    def get_all_scores_for_all_timespans(cls, gradebook_id):
        enddates = (cls.objects
                    .distinct('end_date')
                    .values_list('end_date', flat=True))

        startdate = cls.objects.first().start_date

        return [cls.get_all_scores_for_gradebook_in_timespan(
            gradebook_id, startdate, enddate,
        ) for enddate in enddates]

    class Meta:
        unique_together = ('student_id',
                           'category_id',
                           'start_date',
                           'end_date')


class StudentWeekGradebookScore(AbstractScoreModel):
    
    class Meta:
        unique_together = ('student_id',
                           'gradebook_id',
                           'start_date',
                           'end_date')
