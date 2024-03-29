# Generated by Django 3.2.19 on 2023-05-26 12:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    if getattr(settings, 'TESTING_MIGRATIONS', False):
        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
            ('eox_nelp', '0002_upcomingcourseduedate'),
        ]
        course_overview_model = 'eox_nelp.courseoverview'
    else:
        dependencies = [
            ('course_overviews', '0025_auto_20210702_1602'),
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
            ('eox_nelp', '0002_upcomingcourseduedate'),
        ]
        course_overview_model = 'course_overviews.courseoverview'

    operations = [
        migrations.CreateModel(
            name='FeedbackUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_content', models.IntegerField(blank=True, choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], null=True)),
                ('feedback', models.CharField(blank=True, max_length=500, null=True)),
                ('public', models.BooleanField(default=True, null=True)),
                ('item_id', opaque_keys.edx.django.models.UsageKeyField(max_length=255)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=course_overview_model)),
            ],
            options={
                'unique_together': {('author', 'item_id')},
            },
        ),
        migrations.CreateModel(
            name='FeedbackCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_content', models.IntegerField(blank=True, choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], null=True)),
                ('feedback', models.CharField(blank=True, max_length=500, null=True)),
                ('public', models.BooleanField(default=True, null=True)),
                ('rating_instructors', models.IntegerField(blank=True, choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], null=True)),
                ('recommended', models.BooleanField(default=True, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=course_overview_model)),
            ],
            options={
                'unique_together': {('author', 'course_id')},
            },
        ),
    ]
