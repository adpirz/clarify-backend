# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-08-15 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentweekcategoryscore',
            name='user_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentweekgradebookscore',
            name='user_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
