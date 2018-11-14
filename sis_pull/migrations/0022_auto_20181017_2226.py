# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-10-17 22:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import sis_pull.models


class Migration(migrations.Migration):

    dependencies = [
        ('sis_pull', '0021_scores'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('is_excused', models.BooleanField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('entry', models.CharField(blank=True, max_length=255, null=True)),
                ('is_valid', models.BooleanField()),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis_pull.Assignment')),
                ('gradebook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis_pull.Gradebook')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sis_pull.Student')),
            ],
            bases=(sis_pull.models.SourceObjectMixin, models.Model),
        ),
        migrations.DeleteModel(
            name='Scores',
        ),
    ]