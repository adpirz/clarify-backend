# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-10 18:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis_pull', '0018_auto_20180710_1837'),
    ]

    operations = [
        migrations.RenameModel('usertermroleaffinity', 'stafftermroleaffinity')
    ]