"""Backend for certificates module.
This file contains all the necessary certificates dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/certificates
"""
from lms.djangoapps.certificates import admin  # pylint: disable=import-error


def get_generated_certificates_admin():
    """Allow to get the openedX GeneratedCertificateAdmin class.
    https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/certificates/admin.py

    Returns:
        GeneratedCertificateAdmin class.
    """
    return admin.GeneratedCertificateAdmin
