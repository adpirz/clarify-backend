# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-27 12:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0012_auto_20181127_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clevercode',
            name='code',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
