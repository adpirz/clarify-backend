# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-06 05:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deltas', '0011_auto_20181106_0443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorygradecontextrecord',
            name='average_points_earned',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='categorygradecontextrecord',
            name='total_points_possible',
            field=models.FloatField(default=0.0),
        ),
    ]
