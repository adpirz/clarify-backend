# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Standards(models.Model):
    standard_id = models.IntegerField(primary_key=True)
    parent_standard_id = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    subject_id = models.IntegerField(blank=True, null=True)
    guid = models.CharField(max_length=255, blank=True, null=True)
    state_num = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    seq = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    placeholder = models.NullBooleanField()
    organizer = models.CharField(max_length=255, blank=True, null=True)
    linkable = models.NullBooleanField()
    stem = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lft = models.IntegerField(blank=True, null=True)
    rgt = models.IntegerField(blank=True, null=True)
    custom_code = models.CharField(max_length=200, blank=True, null=True)


class StandardsCache(models.Model):
    cache_id = models.AutoField(primary_key=True)
    gradebook_id = models.ForeignKey(Gradebooks)
    student = models.ForeignKey(Students)
    standard = models.ForeignKey(Standards)
    percentage = models.FloatField(blank=True, null=True)
    mark = models.CharField(max_length=255, blank=True, null=True)
    points_earned = models.FloatField(blank=True, null=True)
    possible_points = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    missing_count = models.IntegerField(blank=True, null=True)
    assignment_count = models.IntegerField(blank=True, null=True)
    zero_count = models.IntegerField(blank=True, null=True)
    excused_count = models.IntegerField(blank=True, null=True)
    timeframe_start_date = models.DateField()
    timeframe_end_date = models.DateField()
    calculated_at = models.DateTimeField()


class States(models.Model):
    state_id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=255)
    sort_order = models.IntegerField(blank=True, null=True)
    country_code = models.CharField(max_length=6, blank=True, null=True)


class Subjects(models.Model):
    subject_id = models.IntegerField(primary_key=True)
    document = models.CharField(max_length=225, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    guid = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    seq = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    hidden = models.NullBooleanField()
    locale = models.CharField(max_length=-1, blank=True, null=True)
    is_custom = models.NullBooleanField()
    state = models.IntegerField(blank=True, null=True)
