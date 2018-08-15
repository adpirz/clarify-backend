from django.db import models


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
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        abstract = True


class StudentWeekCategoryScore(AbstractScoreModel):
    category_id = models.IntegerField()
    category_name = models.CharField(max_length=200)
    category_weight = models.FloatField()
    
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
