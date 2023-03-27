# Generated by Django 3.2.13 on 2023-02-28 22:47

import django.db.models.deletion
import opaque_keys.edx.django.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course_overviews', '0025_auto_20210702_1602'),
    ]

    if getattr(settings, 'TESTING_MIGRATIONS', False):
        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ]
        course_overview_model = 'eox_nelp.courseoverview'
    else:
        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
            ('course_overviews', '0025_auto_20210702_1602'),
        ]
        course_overview_model = 'course_overviews.courseoverview'

    operations = [
        migrations.CreateModel(
            name='ReportUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(blank=True, choices=[('SC', 'Sexual content'), ('GV', 'Graphic violence'), ('HA', 'Hateful or abusive content'), ('CI', 'Copycat or impersonation'), ('OO', 'Other objection')], default=None, max_length=2, null=True)),
                ('item_id', opaque_keys.edx.django.models.UsageKeyField(max_length=255)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=course_overview_model)),
            ],
            options={
                'unique_together': {('author', 'item_id')},
            },
        ),
        migrations.CreateModel(
            name='ReportCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(blank=True, choices=[('SC', 'Sexual content'), ('GV', 'Graphic violence'), ('HA', 'Hateful or abusive content'), ('CI', 'Copycat or impersonation'), ('OO', 'Other objection')], default=None, max_length=2, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=course_overview_model)),
            ],
            options={
                'unique_together': {('author', 'course_id')},
            },
        ),
        migrations.CreateModel(
            name='LikeDislikeUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(null=True)),
                ('item_id', opaque_keys.edx.django.models.UsageKeyField(max_length=255)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=course_overview_model)),
            ],
            options={
                'unique_together': {('author', 'item_id')},
            },
        ),
        migrations.CreateModel(
            name='LikeDislikeCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=course_overview_model)),
            ],
            options={
                'unique_together': {('author', 'course_id')},
            },
        ),
    ]
    testing_models = [
        migrations.CreateModel(
            name='CourseOverview',
            fields=[
                (
                    'id',
                    opaque_keys.edx.django.models.CourseKeyField(
                        db_index=True,
                        primary_key=True,
                        max_length=255,
                        verbose_name='ID',
                    ),
                ),
            ],
        ),
    ]

    if getattr(settings, 'TESTING_MIGRATIONS', False):
        operations = testing_models + operations
