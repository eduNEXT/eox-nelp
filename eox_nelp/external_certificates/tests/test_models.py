"""
Test suite for models in the external_certificates models.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.external_certificates.models import ExternalCertificate

User = get_user_model()


class ExternalCertificateTest(TestCase):
    """
    Test case for the ExternalCertificate model.
    """
    def setUp(self) -> None:
        self.user, _ = User.objects.get_or_create(username="certerman")
        self.course_overview, _ = CourseOverview.objects.get_or_create(id="course-v1:test+Cx108+2024_T4")

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
            course_overview=self.course_overview,
            certificate_url_en="https://example.com/certificate_en",
            certificate_url_ar="https://example.com/certificate_ar",
        )

        self.assertEqual(
            str(certificate),
            f"Certificate {certificate.certificate_id} for user {self.user} and course_overview {self.course_overview}",
        )

    def test_create_external_certificate_from_certificate_response_success(self):
        """
        Test the create_external_certificate_from_certificate_response method of the ExternalCertificate model.

        Expected behavior:
            - Succesful log for certificate creation.
            - The external_certificate object created match the user.
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
                user=self.user,
                course_overview=self.course_overview,
            )

        self.assertIn(
            (
                f"External certificate with ID {certificate_response['certificate_id']} "
                f"created successfully for user {self.user} and course {self.course_overview}."
            ),
            log.output[0]
        )
        self.assertEqual(external_certificate.user, self.user)
        self.assertEqual(external_certificate.course_overview, self.course_overview)
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
                user=self.user,
                course_overview=self.course_overview,
            )

        self.assertIn(
            f"Failed to create external certificate for user {self.user} and course {self.course_overview}. "
            f"certificate_response: {certificate_response}",
            log.output[0]
        )
        self.assertIsNone(external_certificate)
