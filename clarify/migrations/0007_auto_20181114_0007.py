# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-14 00:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0006_staffsectionrecord_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='possible_points',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='possible_score',
            field=models.FloatField(null=True),
        ),
    ]