"""General tests functions and classes for api_clients module.

Classes:
    BasicApiClientMixin: Basic tests that can be implement by AbstractApiClient children.
"""
from django.conf import settings
from django.core.cache import cache
from mock import Mock, patch
from oauthlib.oauth2 import MissingTokenError

from eox_nelp import api_clients
from eox_nelp.api_clients import AbstractApiClient


class BasicApiClientMixin:
    """Basic API client tests."""

    def tearDown(self):  # pylint: disable=invalid-name
        """Clear cache after each test case"""
        cache.clear()

    def test_failed_authentication(self):
        """Test case for invalid credentials.

        Expected behavior:
            - Raise MissingTokenError exception
        """
        self.assertRaises(MissingTokenError, self.api_class)

    @patch("eox_nelp.api_clients.OAuth2Session")
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

        api_client = self.api_class()

        self.assertTrue(hasattr(api_client, "session"))
        self.assertTrue("Authorization" in api_client.session.headers)
        fetch_token_mock.assert_called_with(
            token_url=authentication_url,
            client_secret=client_secret,
            include_client_id=True,
        )

    @patch("eox_nelp.api_clients.requests")
    @patch.object(AbstractApiClient, "_authenticate")
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
        api_client = self.api_class()

        response = api_client.make_post("fake/path", data)

        self.assertDictEqual(response, expected_value)
        requests_mock.Session.return_value.post.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            json=data,
        )

    @patch("eox_nelp.api_clients.requests")
    @patch.object(AbstractApiClient, "_authenticate")
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
        api_client = self.api_class()

        with self.assertLogs(api_clients.__name__, level="ERROR") as logs:
            response = api_client.make_post("fake/path", data)

        self.assertDictEqual(response, {'error': True, 'message': 'Invalid response with status 400'})
        requests_mock.Session.return_value.post.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            json=data,
        )
        self.assertEqual(logs.output, [
            f"ERROR:{api_clients.__name__}:{log_error}"
        ])

    @patch("eox_nelp.api_clients.requests")
    @patch.object(AbstractApiClient, "_authenticate")
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
        api_client = self.api_class()

        response = api_client.make_get("field-options/vocabulary/language", params)

        self.assertDictEqual(response, expected_value)
        requests_mock.Session.return_value.get.assert_called_with(
            url=f"{api_client.base_url}/field-options/vocabulary/language",
            params=params,
        )

    @patch("eox_nelp.api_clients.requests")
    @patch.object(AbstractApiClient, "_authenticate")
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
        api_client = self.api_class()

        with self.assertLogs(api_clients.__name__, level="ERROR") as logs:
            response = api_client.make_get("fake/path", params)

        self.assertDictEqual(response, {'error': True, 'message': 'Invalid response with status 404'})
        requests_mock.Session.return_value.get.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            params=params,
        )
        self.assertEqual(logs.output, [
            f"ERROR:{api_clients.__name__}:{log_error}"
        ])
