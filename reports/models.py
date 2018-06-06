from django.utils import timezone
from django.db import models
from sis_pull.models import Staff


class Report(models.Model):
    staff = models.ForeignKey(Staff)
    title = models.CharField(max_length=100, null=True)
    query = models.TextField(null=False)
    source_report = models.ForeignKey("Report", null=True)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('staff', 'query',)


class Worksheet(models.Model):
    staff = models.ForeignKey(Staff)
    title = models.CharField(max_length=100)
    reports = models.ManyToManyField(Report, through="WorksheetMembership")
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)


class WorksheetMembership(models.Model):
    report = models.ForeignKey(Report)
    worksheet = models.ForeignKey(Worksheet)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('report', 'worksheet',)
