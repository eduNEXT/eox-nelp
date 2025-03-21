"""
Module for testing the external certificates manager API views.
Test classes:
- UpsertExternalCertificateViewTests: Test case for the upsert_external_certificate view.
"""
from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.urls import reverse
from edx_rest_framework_extensions.permissions import JwtHasScope
from mock import patch
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

User = get_user_model()


@ddt
class UpsertExternalCertificateViewTests(APITestCase):
    """
    Test case for the upsert_external_certificate view.
    """
    def setUp(self):
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(username="vader", email="test@mail.com")
        self.course_id = "course-v1:TEST+POWER+2024_T4"
        self.course_overview, _ = CourseOverview.objects.get_or_create(id=self.course_id)
        self.client.force_authenticate(self.user)
        self.url = reverse("external-certificates-api:v1:upsert-external-certificate")

    @patch.object(JwtHasScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_success(self, _):
        """Test successful creation/update of an external certificate.
        Expected behavior:
            - The view should return a 201 CREATED response.
            - The response should contain the certificate ID and URLs.
        """
        request_data = {
            "user_id": self.user.id,
            "course_id": self.course_id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {
            'id': 1,
            'certificate_id': 'TEST25YO59VV76QL',
            'certificate_url_en': 'https://example.com/certificate-en.pdf',
            'certificate_url_ar': 'https://example.com/certificate-ar.pdf',
            'created_at': '2025-03-12T12:24:33.759224',
            'user': str(self.user.id),
            'course_overview': self.course_id,
        }

        with self.assertLogs("eox_nelp.external_certificates.models", level="INFO"):
            response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key, value in expected_response_data.items():
            if key != "created_at":
                self.assertEqual(response.json()[key], value)

    @patch.object(JwtHasScope, 'has_permission', return_value=False)
    def test_upsert_external_certificate_wrong_permission(self, _):
        """Test successful creation/update of an external certificate.
        Expected behavior:
            - The view should return a 403 bad permissions response.
            - Expected error response json.
        """
        request_data = {
            "user_id": self.user.id,
            "course_id": self.course_id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {'detail': 'JWT missing required scopes.'}

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_response_data)

    @data("user_id", "course_id", "certificate_response")
    @patch.object(JwtHasScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_missing_user_id(self, missing_key, _):
        """Test missing required fields. user_id and result_notification_id are missing.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        request_data = {
            "user_id": self.user.id,
            "course_id": self.course_id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        request_data.pop(missing_key)
        expected_response_data = {
            "errors": {
                missing_key: ['This field is required.'],
            }
        }

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response_data)

    @patch.object(JwtHasScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_invalid_user_id(self, _):
        """Test invalid user_id.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        invalid_user_id = 999  # Non-existent ID,
        request_data = {
            "user_id": invalid_user_id,
            "course_id": self.course_id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {
            "error": f'user_id={invalid_user_id} User object with that id doesnt exists'
        }

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response_data)

    @patch.object(JwtHasScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_invalid_course_id(self, _):
        """Test invalid course_id.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        invalid_course_id = "course-v1:INVALID+L3+2025"  # Non-existent ID,
        request_data = {
            "user_id": self.user.id,
            "course_id": invalid_course_id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {
            "error": f'course_id={invalid_course_id} CourseOverview object with that id doesnt exists'
        }

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response_data)

    @patch.object(JwtHasScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_wrong_certificate_response(self, _):
        """Test unsuccesful upsert of an external certificate due error in cert response.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        request_data = {
            "user_id": self.user.id,
            "course_id": self.course_id,
            "certificate_response": {
                "message": "error certificate",
                "error": True,
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response = {
            "error":
                f'External Certificate could not be created for user_id {request_data["user_id"]} '
                f'and course_id {request_data["course_id"]} '
                f'with certificate_response {request_data["certificate_response"]}'
        }

        with self.assertLogs("eox_nelp.external_certificates.models", level="ERROR"):
            response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response)
