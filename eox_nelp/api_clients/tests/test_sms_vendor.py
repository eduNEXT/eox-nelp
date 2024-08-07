"""This file contains all the test for sms_vendor api client file.

Classes:
    TestSMSVendorApiClient: Test for eox-nelp/api_clients/sms_vendor.py.
"""
import unittest

from mock import Mock, patch

from eox_nelp.api_clients.sms_vendor import SMSVendorApiClient
from eox_nelp.api_clients.tests.mixins import TestRestApiClientMixin


class TestSMSVendorApiClient(TestRestApiClientMixin, unittest.TestCase):
    """Tests SMSVendorApiClient"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.api_class = SMSVendorApiClient

    @patch.object(SMSVendorApiClient, "make_post")
    @patch.object(SMSVendorApiClient, "_authenticate", Mock())
    def test_send_sms(self, post_mock):
        """Test successful post request.

        Expected behavior:
            - Response is the expected value
        """
        expected_value = {
            "message": "Operation completed successfully",
            "transaction_id": "50693df-665d-47e1-affb-01076a83b9023427",
            "recipient": "+573219990000",
            "timestamp": "1720220972275"
        }
        post_mock.return_value = expected_value
        recipient = "+573219990000"
        message = "This is a message to test SMS integration."
        api_client = self.api_class()
        expected_payload = {
            "sms_message": message,
            "recipient_number": recipient,
        }

        response = api_client.send_sms(recipient, message)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("sms/send", expected_payload)
