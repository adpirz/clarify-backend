# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-14 00:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0007_auto_20181114_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='sis_id',
            field=models.IntegerField(null=True),
        ),
    ]
