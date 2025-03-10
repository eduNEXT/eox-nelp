"""
Test suite for models in the external_certificates models.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from eox_nelp.external_certificates.models import ExternalCertificate

User = get_user_model()


class ExternalCertificateTest(TestCase):
    """
    Test case for the ExternalCertificate model.
    """
    def setUp(self) -> None:
        self.user, _ = User.objects.get_or_create(username="certerman")
        return super().setUp()

    def test_str_method(self):
        """
        Test the __str__ method of the ExternalCertificate model.

        Expected behavior:
            - The string representation should include the certificate_id and the user's full name.
        """
        certificate = ExternalCertificate.objects.create(  # pylint: disable=no-member
            certificate_id="CERT123",
            user=self.user,
            group_code="13423",
            certificate_url_en="https://example.com/certificate_en",
            certificate_url_ar="https://example.com/certificate_ar",
        )

        self.assertEqual(str(certificate), f"Certificate {certificate.certificate_id} for user {self.user}")

    def test_create_external_certificate_from_certificate_response_success(self):
        """
        Test the create_external_certificate_from_certificate_response method of the ExternalCertificate model.

        Expected behavior:
            - Succesful log for certificate creation.
            - The external_certificate object created match the user.
            - The external_certificate object created match the group_code of certificate_response.
            - The external_certificate object created match the certificate_id of certificate_response.
            - The external_certificate object created match languages.

        """
        certificate_response = {
            "message": "Certificate created successfully",
            "certificate_id": "SREI2412345678",
            "certificate_urls": {
                "en": "https://test.com/storage/pdf/60218/SREI24JEQMGYRLQ3-en-1733337702.pdf",
                "ar": "https://test.com/storage/pdf/60218/SREI24JEQMGYRLQ3-ar-1733337702.pdf",
            },
            "group_code": "3423"
        }

        with self.assertLogs("eox_nelp.external_certificates.models", level="INFO") as log:
            external_certificate = ExternalCertificate.create_external_certificate_from_certificate_response(
                certificate_response=certificate_response,
                user=self.user
            )

        self.assertIn(
            (
                f"External certificate with ID {certificate_response['certificate_id']} "
                f"created successfully for user {self.user}."
            ),
            log.output[0]
        )
        self.assertEqual(external_certificate.user, self.user)
        self.assertEqual(external_certificate.group_code, certificate_response["group_code"])
        self.assertEqual(external_certificate.certificate_id, certificate_response["certificate_id"])
        self.assertEqual(external_certificate.certificate_url_ar, certificate_response["certificate_urls"]["ar"])
        self.assertEqual(external_certificate.certificate_url_en, certificate_response["certificate_urls"]["en"])

    def test_create_external_certificate_from_certificate_response_failure(self):
        """
        Test the create_external_certificate_from_certificate_response method of the ExternalCertificate model.

        Expected behavior:
            - Failure log for certificate creation.
            - The external_certificate object is None
        """
        certificate_response = {
            "error": True,
            "message": "Not allowed certificate",

        }

        with self.assertLogs("eox_nelp.external_certificates.models", level="INFO") as log:
            external_certificate = ExternalCertificate.create_external_certificate_from_certificate_response(
                certificate_response=certificate_response,
                user=self.user
            )

        self.assertIn(
            f"Failed to create external certificate for user {self.user}. certificate_response: {certificate_response}",
            log.output[0]
        )
        self.assertIsNone(external_certificate)
