# Generated by Django 3.2.25 on 2024-09-30 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eox_nelp', '0011_pearsonrtenevent_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='PearsonEngine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rti_triggers', models.PositiveIntegerField(default=0)),
                ('cdd_triggers', models.PositiveIntegerField(default=0)),
                ('ead_triggers', models.PositiveIntegerField(default=0)),
                ('courses', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
