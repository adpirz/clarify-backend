# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-10 18:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis_pull', '0017_auto_20180609_1616'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gradebooksectioncourseaffinity',
            old_name='user',
            new_name='staff',
        ),
        migrations.RenameField(
            model_name='sectionlevelrosterperyear',
            old_name='user',
            new_name='staff',
        ),
        migrations.RenameField(
            model_name='usertermroleaffinity',
            old_name='user',
            new_name='staff',
        ),
    ]
