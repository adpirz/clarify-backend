# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-05 21:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deltas', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='action',
            old_name='public',
            new_name='is_public',
        ),
    ]