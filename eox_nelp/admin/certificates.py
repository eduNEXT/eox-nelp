"""Certificates admin file.
Contains all the nelp admin models for certificates.

Classes:
    NelpGeneratedCertificateAdmin: EoxNelp Certificates admin class.

Functions:
    create_external_certificate_action: Allow to create external certificates.
"""
from django.contrib import admin
from django.utils import timezone
from eox_core.edxapp_wrapper.certificates import get_generated_certificate
from openedx_events.learning.data import CertificateData, CourseData, UserData, UserPersonalData

from eox_nelp.admin.register_admin_model import register_admin_model as register
from eox_nelp.edxapp_wrapper.certificates import GeneratedCertificateAdmin
from eox_nelp.signals.tasks import create_external_certificate
from eox_nelp.signals.utils import _generate_external_certificate_data

GeneratedCertificate = get_generated_certificate()


@admin.action(description="Create external certificates")
def create_external_certificate_action(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    This creates CertificateData and runs the create_external_certificate task for every record
    in the queryset, to allow to create certificates in the external NELP service.

    Args:
        modeladmin: Instance of NelpGeneratedCertificateAdmin
        request: Current django request.
        queryset: Selected records.
    """

    for certificate in queryset:
        certificate_data = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=certificate.user.username,
                    email=certificate.user.email,
                    name=certificate.user.profile.name,
                ),
                id=certificate.user.id,
                is_active=certificate.user.is_active,
            ),
            course=CourseData(
                course_key=certificate.course_id,
            ),
            mode=certificate.mode,
            grade=certificate.grade,
            current_status=certificate.status,
            download_url=certificate.download_url,
            name=certificate.name,
        )
        time = certificate.modified_date.astimezone(timezone.utc)

        create_external_certificate.delay(
            external_certificate_data=_generate_external_certificate_data(
                time=time,
                certificate_data=certificate_data,
            )
        )


class NelpGeneratedCertificateAdmin(GeneratedCertificateAdmin):
    """
    Nelp GeneratedCertificate admin class, this adds the NELP admin custom
    behavior, for the GeneratedCertificate model.
    """
    actions = [create_external_certificate_action]


register(GeneratedCertificate, NelpGeneratedCertificateAdmin)
