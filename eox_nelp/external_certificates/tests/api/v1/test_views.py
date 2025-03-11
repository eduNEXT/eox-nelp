"""
Module for testing the external certificates manager API views.
Test classes:
- UpsertExternalCertificateViewTests: Test case for the upsert_external_certificate view.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from mock import patch
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UpsertExternalCertificateViewTests(APITestCase):
    """
    Test case for the upsert_external_certificate view.
    """
    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(username="vader", email="test@mail.com")
        self.client.force_authenticate(self.user)
        self.url = reverse("external-certificates-api:v1:upsert-external-certificate")

    @patch.object(TokenHasReadWriteScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_success(self, _):
        """Test successful creation/update of an external certificate.
        Expected behavior:
            - The view should return a 201 CREATED response.
            - The response should contain the certificate ID and URLs.
        """
        request_data = {
            "user_id": self.user.id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "group_code": "algo123",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {
            'id': 1,
            'group_code': 'algo123',
            'certificate_id': 'TEST25YO59VV76QL',
            'certificate_url_en': 'https://example.com/certificate-en.pdf',
            'certificate_url_ar': 'https://example.com/certificate-ar.pdf',
            'created_at': '2025-03-12T12:24:33.759224',
            'user': 1,
        }
        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key, value in expected_response_data.items():
            if key != "created_at":
                self.assertEqual(response.json()[key], value)

    @patch.object(TokenHasReadWriteScope, 'has_permission', return_value=False)
    def test_upsert_external_certificate_wrong_permission(self, _):
        """Test successful creation/update of an external certificate.
        Expected behavior:
            - The view should return a 403 bad permissions response.
            - - Expected error response json.
        """
        request_data = {
            "user_id": self.user.id,
            "certificate_response": {
                "message": "Certificate created successfully",
                "group_code": "algo123",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {"detail": "You do not have permission to perform this action."}

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_response_data)

    @patch.object(TokenHasReadWriteScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_missing_user_id(self, _):
        """Test missing required fields. user_id and result_notification_id are missing.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        request_data = {}
        missing_keys = ["certificate_response", "user_id"]
        expected_response_data = {"error": f"Missing required keys: {missing_keys}"}
        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response_data)

    @patch.object(TokenHasReadWriteScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_invalid_user_id(self, _):
        """Test invalid user_id.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        invalid_user_id = 999
        request_data = {
            "user_id": 999,  # Non-existent ID
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://example.com/certificate-en.pdf",
                    "ar": "https://example.com/certificate-ar.pdf",
                },
            },
        }
        expected_response_data = {"error": f'user_id={invalid_user_id} does not match for the certificate'}

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response_data)

    @patch.object(TokenHasReadWriteScope, 'has_permission', return_value=True)
    def test_upsert_external_certificate_wrong_certificate_response(self, _):
        """Test successful creation/update of an external certificate.
        Expected behavior:
            - The view should return a 400 BAD REQUEST response.
            - Expected error response json.
        """
        request_data = {
            "user_id": self.user.id,
            "certificate_response": {
                "error": True,
                "message": "wrong data error",
            },
        }
        expected_response = {
            "error": f'External Certificate could not be created for user_id {request_data["user_id"]}'
                     f'with certificate_response {request_data["certificate_response"]}'
        }

        response = self.client.post(self.url, data=request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_response)
