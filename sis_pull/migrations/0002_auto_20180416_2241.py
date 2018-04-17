# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-16 22:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis_pull', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancedailyrecord',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='categoryscorecache',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='categorytype',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='gradebook',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='gradebooksectioncourseaffinity',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='gradelevel',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='overallscorecache',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sectionlevelrosterperyear',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='staff',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='source_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
