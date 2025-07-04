from django.db import migrations


def update_sc_to_ic(apps, schema_editor):
    """
    Change all 'reason' fields with value 'SC' (Sexual content) to 'IC' (Inappropriate content)
    in both ReportCourse and ReportUnit models.
    """
    ReportCourse = apps.get_model('eox_nelp', 'ReportCourse')
    ReportUnit = apps.get_model('eox_nelp', 'ReportUnit')
    db_alias = schema_editor.connection.alias

    ReportCourse.objects.using(db_alias).filter(reason='SC').update(reason='IC')
    ReportUnit.objects.using(db_alias).filter(reason='SC').update(reason='IC')


def reverse_update_sc_to_ic(apps, schema_editor):
    """
    Revert all 'reason' fields with value 'IC' back to 'SC' in both ReportCourse and ReportUnit models.
    Note: This will change every 'IC' value to 'SC', regardless of its original meaning.
    """
    ReportCourse = apps.get_model('eox_nelp', 'ReportCourse')
    ReportUnit = apps.get_model('eox_nelp', 'ReportUnit')
    db_alias = schema_editor.connection.alias

    ReportCourse.objects.using(db_alias).filter(reason='IC').update(reason='SC')
    ReportUnit.objects.using(db_alias).filter(reason='IC').update(reason='SC')


class Migration(migrations.Migration):

    dependencies = [
        ('eox_nelp', '0015_alter_reportcourse_reason'),
    ]

    operations = [
        migrations.RunPython(update_sc_to_ic, reverse_update_sc_to_ic),
    ]
