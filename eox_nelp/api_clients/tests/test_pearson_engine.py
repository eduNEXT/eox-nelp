"""
Test suite for PearsonEngineApiClient.

This module contains unit tests for the PearsonEngineApiClient class, which
integrates with Pearson Engine services. The tests cover the main methods
import_candidate_demographics, import_exam_authorization, and real_time_import
to ensure they work as expected.

Classes:
    TestPearsonEngineApiClient: Unit test class for PearsonEngineApiClient.
"""
import unittest
from unittest.mock import patch

import requests
from django_countries.fields import Country

from eox_nelp.api_clients.pearson_engine import PearsonEngineApiClient
from eox_nelp.api_clients.tests.mixins import TestOauth2AuthenticatorMixin, TestRestApiClientMixin


class TestPearsonEngineApiClient(TestRestApiClientMixin, TestOauth2AuthenticatorMixin, unittest.TestCase):
    """
    Test suite for PearsonEngineApiClient.

    This class tests the methods of PearsonEngineApiClient, including
    import_candidate_demographics, import_exam_authorization, and real_time_import.
    """

    def setUp(self):
        """
        Set up the test environment.

        This method initializes the API client class for testing.
        """
        self.api_class = PearsonEngineApiClient

    @patch.object(PearsonEngineApiClient, "make_post")
    @patch.object(PearsonEngineApiClient, "_authenticate")
    def test_import_candidate_demographics(self, auth_mock, post_mock):
        """
        Test import_candidate_demographics API call.

        Expected behavior:
            - Response is the expected value.
            - make_post is called with the correct path and payload.
        """
        auth_mock.return_value = requests.Session()
        expected_value = {
            "status": {"success": True},
        }
        post_mock.return_value = expected_value

        user = self._create_test_user()
        api_client = self.api_class()

        response = api_client.import_candidate_demographics(user)

        self.assertDictEqual(response, expected_value)
        # pylint: disable=protected-access
        post_mock.assert_called_with("rti/api/v1/candidate-demographics/", {
            "user_data": api_client._get_user_data(user),
            "platform_data": api_client._get_platform_data(),
        })

    @patch.object(PearsonEngineApiClient, "make_post")
    @patch.object(PearsonEngineApiClient, "_authenticate")
    def test_import_exam_authorization(self, auth_mock, post_mock):
        """
        Test import_exam_authorization API call.

        Expected behavior:
            - Response is the expected value.
            - make_post is called with the correct path and payload.
        """
        auth_mock.return_value = requests.Session()
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        post_mock.return_value = expected_value
        user = self._create_test_user()
        exam_id = "exam-123"
        api_client = self.api_class()

        response = api_client.import_exam_authorization(user, exam_id, transaction_type="Add")

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_with("rti/api/v1/exam-authorization/", {
            "user_data": {"username": user.username},
            "exam_data": api_client._get_exam_data(exam_id),  # pylint: disable=protected-access
            "transaction_type": "Add",
        })

    @patch.object(PearsonEngineApiClient, "make_post")
    @patch.object(PearsonEngineApiClient, "_authenticate")
    def test_real_time_import(self, auth_mock, post_mock):
        """
        Test real_time_import API call.

        Expected behavior:
            - Response is the expected value.
            - make_post is called with the correct path and payload.
        """
        auth_mock.return_value = requests.Session()
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1},
        }
        post_mock.return_value = expected_value
        user = self._create_test_user()
        exam_id = "exam-123"
        api_client = self.api_class()

        response = api_client.real_time_import(user, exam_id)

        self.assertDictEqual(response, expected_value)
        # pylint: disable=protected-access
        post_mock.assert_called_with("rti/api/v1/exam-authorization/", {
            "user_data": api_client._get_user_data(user),
            "exam_data": api_client._get_exam_data(exam_id),
            "platform_data": api_client._get_platform_data(),
        })

    def _create_test_user(self):
        """
        Create a mock user for testing.

        Returns:
            user: A mock user object with necessary attributes.
        """
        # pylint: disable=missing-class-docstring
        class MockUser:
            username = "testuser"
            first_name = "Test"
            last_name = "User"
            email = "testuser@example.com"

            class Profile:
                country = Country("US")
                city = "New York"
                phone_number = "+1234567890"
                mailing_address = "123 Test St"

            class ExtraInfo:
                arabic_first_name = "اختبار"
                arabic_last_name = "مستخدم"

            profile = Profile()
            extrainfo = ExtraInfo()

        return MockUser()
