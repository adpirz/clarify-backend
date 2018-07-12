from django.utils import timezone
from django.db import models
from sis_pull.models import Staff


class Report(models.Model):
    staff = models.ForeignKey(Staff)
    title = models.CharField(max_length=100, null=True, blank=True)
    query = models.TextField(null=False)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else self.query

    class Meta:
        unique_together = ('staff', 'query',)


class Worksheet(models.Model):
    staff = models.ForeignKey(Staff)
    title = models.CharField(max_length=100)
    reports = models.ManyToManyField(Report, through="WorksheetMembership")
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class WorksheetMembership(models.Model):
    report = models.ForeignKey(Report)
    worksheet = models.ForeignKey(Worksheet)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('report', 'worksheet',)


class ReportShare(models.Model):
    parent = models.ForeignKey(Report, related_name="parent", null=True, blank=True)
    child = models.ForeignKey(Report, related_name="child")
    by = models.ForeignKey(Staff)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('parent', 'child',)
