# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-12-11 08:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0023_assignment_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='gradebook',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='score',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='term',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sis_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
    ]