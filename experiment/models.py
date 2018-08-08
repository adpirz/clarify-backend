from django.db import models

from sis_mirror.models import Categories, Gradebooks, Students


class AbstractScoreModel(models.Model):
    student = models.IntegerField()
    student_name = models.CharField(max_length=200)
    mark = models.CharField(max_length=3, blank=True)
    percentage = models.FloatField(null=True)
    possible_points = models.FloatField(null=True)
    number_of_assignments = models.IntegerField(default=0)
    number_of_missing_assignments = models.IntegerField(default=0)
    gradebook = models.IntegerField()
    gradebook_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        abstract = True


class StudentWeekCategoryScore(AbstractScoreModel):
    category = models.IntegerField()
    category_name = models.CharField(max_length=200)
    category_weight = models.FloatField()
    
    class Meta:
        unique_together = ('student', 'category', 'start_date', 'end_date')


class StudentWeekGradebookScore(AbstractScoreModel):
    
    class Meta:
        unique_together = ('student', 'gradebook', 'start_date', 'end_date')
