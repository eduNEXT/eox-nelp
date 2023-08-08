"""This file contains all the test for futurex api client file.

Classes:
    TestFuturexApiClient: Test for eox-nelp/api_clients/futurex.py.
"""
import unittest

import requests
from mock import patch

from eox_nelp.api_clients.futurex import FuturexApiClient, FuturexMissingArguments
from eox_nelp.api_clients.tests import TestOauth2ApiClientMixin


class TestFuturexApiClient(TestOauth2ApiClientMixin, unittest.TestCase):
    """Tests FuturexApiClient"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.api_class = FuturexApiClient

    @patch.object(FuturexApiClient, "make_post")
    @patch.object(FuturexApiClient, "_authenticate")
    def test_enrollment_progress(self, auth_mock, post_mock):
        """Test enrollment progress API call.

        Expected behavior:
            - Response is the expected value
            - make_post was called with the right values.
        """
        auth_mock.return_value = requests.Session()
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        post_mock.return_value = expected_value
        data = {
            "courseId": "course-v1:lms152",
            "userId": 52,
            "approxTotalCourseHrs": 5,
            "overallProgress": 10,
            "membershipState": "active",
            "enrolledAt": "2012-12-30",
            "isCompleted": False,
        }
        api_client = self.api_class()

        response = api_client.enrollment_progress(data)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_with("enrollment-progress", data)

    @patch.object(FuturexApiClient, "_authenticate")
    def test_failed_enrollment_progress(self, auth_mock):
        """Test when enrollment progress fails due to missing parameters.

        Expected behavior:
            - Raise FuturexMissingArguments exception
        """
        auth_mock.return_value = requests.Session()
        data = {
            "courseId": "course-v1:lms152",
            "userId": 52,
            "approxTotalCourseHrs": 5,
        }
        api_client = self.api_class()

        self.assertRaises(FuturexMissingArguments, api_client.enrollment_progress, data)
