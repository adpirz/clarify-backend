# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-08 04:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0029_auto_20190109_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
