# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-13 15:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0004_auto_20181113_0546'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionGradeLevels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_level', models.CharField(choices=[('PK', 'Pre-Kindergarten'), ('K', 'Kindergarten'), ('1', '1st Grade'), ('2', '2nd Grade'), ('3', '3rd Grade'), ('4', '4th Grade'), ('5', '5th Grade'), ('6', '6th Grade'), ('7', '7th Grade'), ('8', '8th Grade'), ('9', '9th Grade'), ('10', '10th Grade'), ('11', '11th Grade'), ('12', '12th Grade')], max_length=2)),
            ],
        ),
        migrations.RemoveField(
            model_name='section',
            name='grade_level',
        ),
        migrations.AddField(
            model_name='sectiongradelevels',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clarify.Section'),
        ),
    ]