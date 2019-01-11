# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-01-09 22:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clarify', '0028_auto_20190109_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='googleauth',
            name='id_token',
            field=models.CharField(blank=True, max_length=250, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='googleauth',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='clarify.UserProfile'),
        ),
    ]
