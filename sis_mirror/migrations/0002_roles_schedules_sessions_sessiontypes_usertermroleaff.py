# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-18 20:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis_mirror', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('role_id', models.IntegerField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=255)),
                ('role_level', models.IntegerField(blank=True, null=True)),
                ('can_teach', models.BooleanField()),
                ('can_counsel', models.BooleanField()),
                ('job_classification_id', models.IntegerField(blank=True, null=True)),
                ('role_short_name', models.CharField(blank=True, max_length=255, null=True)),
                ('system_key', models.CharField(blank=True, max_length=255, null=True)),
                ('system_key_sort', models.IntegerField(blank=True, null=True)),
                ('can_refer_discipline', models.BooleanField()),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'roles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Schedules',
            fields=[
                ('schedule_id', models.IntegerField(primary_key=True, serialize=False)),
                ('created_by', models.IntegerField(blank=True, null=True)),
                ('last_modified_by', models.IntegerField(blank=True, null=True)),
                ('schedule_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_mod_time', models.IntegerField(blank=True, null=True)),
                ('creation_time', models.IntegerField(blank=True, null=True)),
                ('session_id', models.IntegerField()),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('deleted_by', models.IntegerField(blank=True, null=True)),
                ('is_locked', models.NullBooleanField()),
            ],
            options={
                'db_table': 'schedules',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False)),
                ('academic_year', models.IntegerField()),
                ('field_positive_attendance', models.BooleanField(db_column='_positive_attendance')),
                ('elementary_grade_levels', models.TextField()),
                ('district_reports', models.BooleanField()),
                ('attendance_program_set_id', models.IntegerField()),
                ('is_high_poverty', models.BooleanField()),
                ('is_remote_and_necessary', models.BooleanField()),
                ('exclude_from_p223', models.BooleanField()),
                ('is_open_doors_youth_reengagement_program_school', models.BooleanField()),
                ('is_online_instruction', models.BooleanField()),
            ],
            options={
                'db_table': 'sessions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SessionTypes',
            fields=[
                ('code_id', models.AutoField(primary_key=True, serialize=False)),
                ('code_key', models.CharField(max_length=255)),
                ('code_translation', models.CharField(blank=True, max_length=255, null=True)),
                ('system_key', models.CharField(blank=True, max_length=255, null=True)),
                ('system_key_sort', models.IntegerField(blank=True, null=True)),
                ('state_id', models.CharField(blank=True, max_length=255, null=True)),
                ('sort_order', models.IntegerField(blank=True, null=True)),
                ('system_state_id', models.IntegerField(blank=True, null=True)),
                ('system_key_translation', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'session_types',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserTermRoleAff',
            fields=[
                ('utra_id', models.AutoField(primary_key=True, serialize=False)),
                ('last_schedule_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'user_term_role_aff',
                'managed': False,
            },
        ),
    ]
