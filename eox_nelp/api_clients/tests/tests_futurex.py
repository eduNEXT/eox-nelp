"""This file contains all the test for futurex api client file.
Classes:
    LikeDislikeUnitExperienceTestCase: Test LikeDislikeUnitExperienceView.
"""
import unittest

from django.conf import settings
from django.core.cache import cache
from mock import Mock, patch
from oauthlib.oauth2 import MissingTokenError

from eox_nelp.api_clients import futurex
from eox_nelp.api_clients.futurex import FuturexApiClient, FuturexMissingArguments


class TestFuturexApiclient(unittest.TestCase):
    """Tests FuturexApiClient"""

    def tearDown(self):
        cache.clear()

    def test_failed_authentication(self):
        """Test case for invalid credentials.

        Expected behavior:
            - Raise MissingTokenError exception
        """
        self.assertRaises(MissingTokenError, FuturexApiClient)

    @patch("eox_nelp.api_clients.futurex.OAuth2Session")
    def test_successful_authentication(self, oauth2_session_mock):
        """Test case when the authentication response is valid.

        Expected behavior:
            - Session is set
            - Session headers contains Authorization key.
            - fetch_token was called with the right values.
        """
        fetch_token_mock = Mock()
        fetch_token_mock.return_value = {
            "token_type": "Bearer",
            "access_token": "12345678abc",
            "expires_in": 200,
        }
        oauth2_session_mock.return_value.fetch_token = fetch_token_mock
        authentication_url = f"{settings.FUTUREX_API_URL}/oauth/token"
        client_secret = settings.FUTUREX_API_CLIENT_SECRET

        api_client = FuturexApiClient()

        self.assertTrue(hasattr(api_client, "session"))
        self.assertTrue("Authorization" in api_client.session.headers)
        fetch_token_mock.assert_called_with(
            token_url=authentication_url,
            client_secret=client_secret,
            include_client_id=True,
        )

    @patch("eox_nelp.api_clients.futurex.requests")
    @patch.object(FuturexApiClient, "_authenticate")
    def test_successful_post(self, auth_mock, requests_mock):
        """Test case when a POST request success.

        Expected behavior:
            - Response is the expected value
            - POST was called with the given data and right url.
        """
        auth_mock.return_value = {}
        response = Mock()
        response.status_code = 200
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        response.json.return_value = expected_value
        requests_mock.Session.return_value.post.return_value = response
        data = {"testing": True, "application": "futurex"}
        api_client = FuturexApiClient()

        response = api_client.make_post("fake/path", data)

        self.assertDictEqual(response, expected_value)
        requests_mock.Session.return_value.post.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            json=data,
        )

    @patch("eox_nelp.api_clients.futurex.requests")
    @patch.object(FuturexApiClient, "_authenticate")
    def test_failed_post(self, auth_mock, requests_mock):
        """Test case when a POST request fails.

        Expected behavior:
            - Response is an empty dict
            - POST was called with the given data and right url.
            - Error was logged.
        """
        auth_mock.return_value = {}
        response = Mock()
        response.status_code = 400
        response.json.return_value = {"test": True}
        requests_mock.Session.return_value.post.return_value = response
        data = {"testing": True, "application": "futurex"}
        log_error = (
            "An error has occurred trying to make post request to https://testing.com/fake/path with status code 400"
        )
        api_client = FuturexApiClient()

        with self.assertLogs(futurex.__name__, level="ERROR") as logs:
            response = api_client.make_post("fake/path", data)

        self.assertDictEqual(response, {})
        requests_mock.Session.return_value.post.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            json=data,
        )
        self.assertEqual(logs.output, [
            f"ERROR:{futurex.__name__}:{log_error}"
        ])

    @patch("eox_nelp.api_clients.futurex.requests")
    @patch.object(FuturexApiClient, "_authenticate")
    def test_successful_get(self, auth_mock, requests_mock):
        """Test case when a GET request success.

        Expected behavior:
            - Response is the expected value
            - GET was called with the given data and right url.
        """
        auth_mock.return_value = {}
        response = Mock()
        response.status_code = 200
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        response.json.return_value = expected_value
        requests_mock.Session.return_value.get.return_value = response
        params = {"format": "json"}
        api_client = FuturexApiClient()

        response = api_client.make_get("field-options/vocabulary/language", params)

        self.assertDictEqual(response, expected_value)
        requests_mock.Session.return_value.get.assert_called_with(
            url=f"{api_client.base_url}/field-options/vocabulary/language",
            params=params,
        )

    @patch("eox_nelp.api_clients.futurex.requests")
    @patch.object(FuturexApiClient, "_authenticate")
    def test_failed_get(self, auth_mock, requests_mock):
        """Test case when a GET request fails.

        Expected behavior:
            - Response is an empty dict
            - GET was called with the given data and right url.
            - Error was logged.
        """
        auth_mock.return_value = {}
        response = Mock()
        response.status_code = 404
        response.json.return_value = {"test": True}
        requests_mock.Session.return_value.get.return_value = response
        params = {"format": "json"}
        log_error = (
            "An error has occurred trying to make a get request to https://testing.com/fake/path with status code 404"
        )
        api_client = FuturexApiClient()

        with self.assertLogs(futurex.__name__, level="ERROR") as logs:
            response = api_client.make_get("fake/path", params)

        self.assertDictEqual(response, {})
        requests_mock.Session.return_value.get.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            params=params,
        )
        self.assertEqual(logs.output, [
            f"ERROR:{futurex.__name__}:{log_error}"
        ])

    @patch.object(FuturexApiClient, "make_post")
    @patch.object(FuturexApiClient, "_authenticate")
    def test_enrollment_progress(self, auth_mock, post_mock):
        """Test enrollment progress API call.

        Expected behavior:
            - Response is the expected value
            - make_post was called with the right values.
        """
        auth_mock.return_value = {}
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
        api_client = FuturexApiClient()

        response = api_client.enrollment_progress(data)

        self.assertDictEqual(response, expected_value)
        post_mock.assert_called_with("enrollment-progress", data)

    @patch.object(FuturexApiClient, "_authenticate")
    def test_failed_enrollment_progress(self, auth_mock):
        """Test when enrollment progress fails due to missing parameters.

        Expected behavior:
            - Raise FuturexMissingArguments exception
        """
        auth_mock.return_value = {}
        data = {
            "courseId": "course-v1:lms152",
            "userId": 52,
            "approxTotalCourseHrs": 5,
        }
        api_client = FuturexApiClient()

        self.assertRaises(FuturexMissingArguments, api_client.enrollment_progress, data)
