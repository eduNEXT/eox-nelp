"""This file contains all the test for sms_vendor api client file.

Classes:
    TestSMSVendorApiClient: Test for eox-nelp/api_clients/sms_vendor.py.
"""
import unittest

from django.conf import settings
from mock import patch

from eox_nelp.api_clients.sms_vendor import SMSVendorApiClient
from eox_nelp.api_clients.tests.mixins import TestRestApiClientMixin


class TestSMSVendorApiClient(TestRestApiClientMixin, unittest.TestCase):
    """Tests SMSVendorApiClient"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.api_class = SMSVendorApiClient

    @patch.object(SMSVendorApiClient, "make_post")
    def test_send_sms(self, post_mock):
        """Test successful post request.

        Expected behavior:
            - Response is the expected value
        """
        expected_value = {
            "message": "SMS sent =), waiting what would be this field.",
            "responseCode": 200,
        }
        post_mock.return_value = expected_value
        recipient = 3219802890
        message = "This is a message to test SMS integration."
        api_client = self.api_class()
        expected_payload = {
            "message": message,
            "number": recipient,
            "username": settings.SMS_VENDOR_USERNAME,
            "password": settings.SMS_VENDOR_PASSWORD,
            "sender": settings.SMS_VENDOR_MSG_SENDER,
        }
        response = api_client.send_sms(recipient, message)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("", expected_payload)
