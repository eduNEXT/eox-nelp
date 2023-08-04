"""This file contains all the test for certificates api client file.

Classes:
    TestExternalCertificatesApiClient: Test for eox-nelp/api_clients/certificates.py.
"""
import unittest

from django.utils import timezone
from mock import patch

from eox_nelp.api_clients.certificates import ExternalCertificatesApiClient
from eox_nelp.api_clients.tests import BasicApiClientMixin


class TestExternalCertificatesApiClient(BasicApiClientMixin, unittest.TestCase):
    """Tests ExternalCertificatesApiClient"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.api_class = ExternalCertificatesApiClient

    @patch.object(ExternalCertificatesApiClient, "make_post")
    @patch.object(ExternalCertificatesApiClient, "_authenticate")
    def test_create_certificate(self, auth_mock, post_mock):
        """Test successful post request.

        Expected behavior:
            - Response is the expected value
        """
        auth_mock.return_value = {}
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        post_mock.return_value = expected_value
        user = {
            "national_id": "10224587",
            "english_name": " Testing",
            "arabic_name": "اختبارات",
        }
        data = {
            "id": "124ABC",
            "created_at": timezone.now(),
            "expiration_date": timezone.now() + timezone.timedelta(days=365),
            "grade": 10,
            "is_passing": True,
            "user": user,
        }
        api_client = self.api_class()

        response = api_client.create_external_certificate(data)

        self.assertDictEqual(response, expected_value)

    @patch.object(ExternalCertificatesApiClient, "_authenticate")
    def test_failed_create_certificate(self, auth_mock):
        """Test when the mandatory fields has not been sent.

        Expected behavior:
            - Raise KeyError exception.
        """
        auth_mock.return_value = {}
        data = {}
        api_client = ExternalCertificatesApiClient()

        self.assertRaises(KeyError, api_client.create_external_certificate, data)
