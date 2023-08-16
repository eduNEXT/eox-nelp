"""Backend for certificates module.
This file contains all the necessary certificates dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/certificates
"""
from django.apps import apps
from django.contrib import admin
from lms.djangoapps import certificates  # pylint: disable=import-error


def get_generated_certificates_admin():
    """Allow to get the openedX GeneratedCertificateAdmin class.
    https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/certificates/admin.py

    Returns:
        GeneratedCertificateAdmin class.
    """
    if apps.is_installed(certificates.models.__package__):
        return certificates.admin.GeneratedCertificateAdmin

    return admin.ModelAdmin
