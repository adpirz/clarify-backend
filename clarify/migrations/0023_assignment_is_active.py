# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-12-11 08:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0022_merge_20181211_0234'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='is_active',
            field=models.NullBooleanField(),
        ),
    ]
