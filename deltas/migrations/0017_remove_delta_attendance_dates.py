# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-13 05:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deltas', '0016_auto_20181112_2331'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='delta',
            name='attendance_dates',
        ),
    ]