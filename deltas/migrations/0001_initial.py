# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-12-11 09:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]
    # dependencies = [
    #     ('clarify', '0024_auto_20181211_0852'),
    # ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('note', 'Note'), ('call', 'Call'), ('message', 'Message')], default='note', max_length=255)),
                ('completed_on', models.DateTimeField(blank=True, null=True)),
                ('due_on', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(blank=True)),
                ('public', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clarify.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryGradeContextRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_points_possible', models.FloatField()),
                ('average_points_earned', models.FloatField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clarify.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Delta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('missing', 'Missing Assignments delta'), ('category', 'Category delta'), ('attendance', 'Attendance delta')], max_length=255)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('category_average_before', models.FloatField(null=True)),
                ('category_average_after', models.FloatField(null=True)),
                ('settled', models.BooleanField(default=False)),
                ('context_record', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='deltas.CategoryGradeContextRecord')),
                ('gradebook', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clarify.Gradebook')),
            ],
        ),
        migrations.CreateModel(
            name='MissingAssignmentRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('missing_on', models.DateField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clarify.Assignment')),
                ('delta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deltas.Delta')),
            ],
        ),
        migrations.AddField(
            model_name='delta',
            name='missing_assignments',
            field=models.ManyToManyField(through='deltas.MissingAssignmentRecord', to='clarify.Assignment'),
        ),
        migrations.AddField(
            model_name='delta',
            name='score',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clarify.Score'),
        ),
        migrations.AddField(
            model_name='delta',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clarify.Student'),
        ),
        migrations.AddField(
            model_name='action',
            name='deltas',
            field=models.ManyToManyField(blank=True, to='deltas.Delta'),
        ),
        migrations.AddField(
            model_name='action',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clarify.Student'),
        ),
        migrations.AlterUniqueTogether(
            name='categorygradecontextrecord',
            unique_together=set([('category', 'date')]),
        ),
    ]
