# Generated by Django 3.2.21 on 2024-06-06 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eox_nelp', '0008_pearsonrtenevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pearsonrtenevent',
            name='event_type',
            field=models.CharField(choices=[('result-notification', 'Result Notification'), ('place-hold', 'Place Hold'), ('release-hold', 'Release Hold'), ('modify-result-status', 'Modify Result Status'), ('revoke-result', 'Revoke Result'), ('unrevoke-result', 'Unrevoke Result'), ('modify-appointment', 'Modify Appointment'), ('cancel-appointment', 'Cancel Appointment')], max_length=20),
        ),
    ]
