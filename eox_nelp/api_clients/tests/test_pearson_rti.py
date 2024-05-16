"""This file contains all the test for pearson_rti api client file.

Classes:
    TestPearsonRTIApiClient: Test for eox-nelp/api_clients/sms_vendor.py.
"""
import unittest

import requests
from bs4 import BeautifulSoup
from mock import patch

from eox_nelp.api_clients import pearson_rti
from eox_nelp.api_clients.pearson_rti import PearsonRTIApiClient
from eox_nelp.api_clients.tests.mixins import TestPKCS12AuthenticatorMixin, TestSOAPClientMixin


class TestPearsonRTIApiClient(TestSOAPClientMixin, TestPKCS12AuthenticatorMixin, unittest.TestCase):
    """Tests PearsonRTIApiClient"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.api_class = PearsonRTIApiClient

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_successful_ping(self, post_mock):
        """Test successful ping request.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
        """
        expected_value = {
            "status": "success",
        }
        post_mock.return_value = BeautifulSoup('<result status="success" env="Prod" inProduction="true"/>', "xml")
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()

        response = api_client.ping(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/Ping", payload)

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_failed_ping(self, post_mock):
        """Test failed ping request.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
        """
        expected_value = {
            "status": "failed",
        }
        post_mock.return_value = BeautifulSoup('<error status="error" env="Prod" inProduction="true"/>', "xml")
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()

        response = api_client.ping(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/Ping", payload)

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_fault_cdd(self, post_mock):
        """Test when the cdd request return error.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
        """
        expected_value = {
            "status": "error",
            "fault_code": "vue:AuthenticationFailure",
            "message": "Invalid user name or password.",
        }
        post_mock.return_value = BeautifulSoup(
            """
                <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                    <soapenv:Fault xmlns:vue="http://ws.pearsonvue.com">
                        <faultcode>vue:AuthenticationFailure</faultcode>
                        <faultstring>Invalid user name or password.</faultstring>
                    </soapenv:Fault>
                </soapenv:Envelope>
            """,
            "xml",
        )
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()

        response = api_client.import_candidate_demographics(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/CDDService", payload)

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_accepted_status_cdd(self, post_mock):
        """Test when the cdd request return an accepted status.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
        """
        expected_value = {
            "status": "accepted",
            "message": "ok",
            "candidate_id": "12345",
            "client_candidate_id": "CC1234",
        }
        post_mock.return_value = BeautifulSoup(
            """
                <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope"
                xmlns:cdd="http://ws.pearsonvue.com/rti/cdd/schema">
                    <cdd:cddResponse candidateID="12345" clientCandidateID="CC1234">
                        <status>Accepted</status>
                        <message>ok</message>
                    </sch:cddResponse>
                </soapenv:Envelope>
            """,
            "xml",
        )
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()

        response = api_client.import_candidate_demographics(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/CDDService", payload)

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_unexpected_cdd_error(self, post_mock):
        """Test when the cdd response returns an unconsider result.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
            - Error was log
        """
        post_mock.return_value = BeautifulSoup('<error status="error" env="Prod" inProduction="true"/>', "xml")
        expected_value = {
            "status": "unexpected error",
            "response": post_mock.return_value,
        }
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()
        log_error = (
            "An unexpected error has occurred trying to make a CDD request getting "
            f"the following response: {post_mock.return_value}"
        )

        with self.assertLogs(pearson_rti.__name__, level="ERROR") as logs:
            response = api_client.import_candidate_demographics(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/CDDService", payload)
        self.assertEqual(logs.output, [
            f"ERROR:{pearson_rti.__name__}:{log_error}"
        ])

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_fault_ead(self, post_mock):
        """Test when the ead request return error.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
        """
        expected_value = {
            "status": "error",
            "fault_code": "vue:AuthenticationFailure",
            "message": "Invalid user name or password.",
        }
        post_mock.return_value = BeautifulSoup(
            """
                <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                    <soapenv:Fault xmlns:vue="http://ws.pearsonvue.com">
                        <faultcode>vue:AuthenticationFailure</faultcode>
                        <faultstring>Invalid user name or password.</faultstring>
                    </soapenv:Fault>
                </soapenv:Envelope>
            """,
            "xml",
        )
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()

        response = api_client.import_exam_authorization(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/EADService", payload)

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_accepted_status_ead(self, post_mock):
        """Test when the ead request return an accepted status.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
        """
        expected_value = {
            "status": "accepted",
            "message": "ok",
            "client_candidate_id": "CC1234",
        }
        post_mock.return_value = BeautifulSoup(
            """
                <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope"
                xmlns:sch="http://ws.pearsonvue.com/rti/ead/schema">
                    <sch:eadResponse authorizationID="1234" clientAuthorizationID="A1234">
                        <clientCandidateID>CC1234</clientCandidateID>
                        <status>Accepted</status>
                        <message>ok</message>
                    </sch:eadResponse>
                </soapenv:Envelope>
            """,
            "xml",
        )
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()

        response = api_client.import_exam_authorization(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/EADService", payload)

    @patch.object(PearsonRTIApiClient, "make_post")
    @patch.object(PearsonRTIApiClient, "_authenticate", requests.Session)
    def test_unexpected_ead_error(self, post_mock):
        """Test when the ead response returns an unconsider result.

        Expected behavior:
            - Response is the expected value.
            - Post request was made with the required parameters.
            - Error was log
        """
        post_mock.return_value = BeautifulSoup('<error status="error" env="Prod" inProduction="true"/>', "xml")
        expected_value = {
            "status": "unexpected error",
            "response": post_mock.return_value,
        }
        payload = "<testing><user>Harry</user></testing>"
        api_client = self.api_class()
        log_error = (
            "An unexpected error has occurred trying to make a EAD request getting "
            f"the following response: {post_mock.return_value}"
        )

        with self.assertLogs(pearson_rti.__name__, level="ERROR") as logs:
            response = api_client.import_exam_authorization(payload)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_once_with("cxfws2/services/EADService", payload)
        self.assertEqual(logs.output, [
            f"ERROR:{pearson_rti.__name__}:{log_error}"
        ])
