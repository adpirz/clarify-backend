# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-29 04:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0019_score_updated_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='due_date',
            field=models.DateField(null=True),
        ),
    ]
