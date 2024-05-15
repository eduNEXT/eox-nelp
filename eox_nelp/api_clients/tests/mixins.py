"""Mixins for multiple test implementations.

Classes:
    TestRestApiClientMixin: Basic tests that can be implemented by AbstractAPIRestClient children.
    TestOauth2AuthenticatorMixin: Basic tests that can be implemented by Oauth2Authenticator children.
    TestBasicAuthAuthenticatorMixin: Basic tests that can be implemented by BasicAuthAuthenticator children.
"""
from django.conf import settings
from django.core.cache import cache
from mock import Mock, patch
from oauthlib.oauth2 import MissingTokenError
from requests.auth import HTTPBasicAuth

from eox_nelp import api_clients


class TestRestApiClientMixin:
    """Basic API client tests."""

    def tearDown(self):  # pylint: disable=invalid-name
        """Clear cache after each test case"""
        cache.clear()

    @patch("eox_nelp.api_clients.authenticators.requests")
    def test_successful_post(self, requests_mock):
        """Test case when a POST request success.

        Expected behavior:
            - Response is the expected value
            - POST was called with the given data and right url.
        """
        response = Mock()
        response.ok = True
        response.status_code = 200
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        response.json.return_value = expected_value
        requests_mock.Session.return_value.post.return_value = response
        data = {"testing": True, "application": "futurex"}

        with patch.object(self.api_class, "_authenticate") as auth_mock:
            auth_mock.return_value = requests_mock.Session()
            api_client = self.api_class()

        response = api_client.make_post("fake/path", data)

        self.assertDictEqual(response, expected_value)
        requests_mock.Session.return_value.post.assert_called_with(
            url=f"{api_client.base_url}/fake/path",
            json=data,
        )

    @patch("eox_nelp.api_clients.authenticators.requests")
    def test_failed_post(self, requests_mock):
        """Test case when a POST request fails.

        Expected behavior:
            - Response is an empty dict
            - POST was called with the given data and right url.
            - Error was logged.
        """
        response = Mock()
        response.ok = False
        response.status_code = 400
        response.json.return_value = {"test": True}
        requests_mock.Session.return_value.post.return_value = response
        data = {"testing": True, "application": "futurex"}
        log_error = (
            "An error has occurred trying to make post request to https://testing.com/fake/path with status code 400 "
            f"and message {response.json()}"
        )
        with patch.object(self.api_class, "_authenticate") as auth_mock:
            auth_mock.return_value = requests_mock.Session()
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

    @patch("eox_nelp.api_clients.authenticators.requests")
    def test_successful_get(self, requests_mock):
        """Test case when a GET request success.

        Expected behavior:
            - Response is the expected value
            - GET was called with the given data and right url.
        """
        response = Mock()
        response.ok = True
        response.status_code = 200
        expected_value = {
            "status": {"success": True, "message": "successful", "code": 1}
        }
        response.json.return_value = expected_value
        requests_mock.Session.return_value.get.return_value = response
        params = {"format": "json"}
        with patch.object(self.api_class, "_authenticate") as auth_mock:
            auth_mock.return_value = requests_mock.Session()
            api_client = self.api_class()

        response = api_client.make_get("field-options/vocabulary/language", params)

        self.assertDictEqual(response, expected_value)
        requests_mock.Session.return_value.get.assert_called_with(
            url=f"{api_client.base_url}/field-options/vocabulary/language",
            params=params,
        )

    @patch("eox_nelp.api_clients.authenticators.requests")
    def test_failed_get(self, requests_mock):
        """Test case when a GET request fails.

        Expected behavior:
            - Response is an empty dict
            - GET was called with the given data and right url.
            - Error was logged.
        """
        response = Mock()
        response.ok = False
        response.status_code = 404
        response.json.return_value = {"test": True}
        requests_mock.Session.return_value.get.return_value = response
        params = {"format": "json"}
        log_error = (
            "An error has occurred trying to make a get request to https://testing.com/fake/path with status code 404 "
            f"and message {response.json()}"
        )
        with patch.object(self.api_class, "_authenticate") as auth_mock:
            auth_mock.return_value = requests_mock.Session()
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


class TestOauth2AuthenticatorMixin:
    """
    This test class contains test cases for the `AbstractOauth2ApiClient` class
    to ensure that the authentication process using OAuth2 is working correctly.
    """

    def test_failed_authentication(self):
        """Test case for invalid credentials.

        Expected behavior:
            - Raise MissingTokenError exception
        """
        self.assertRaises(MissingTokenError, self.api_class)

    @patch("eox_nelp.api_clients.authenticators.OAuth2Session")
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


class TestBasicAuthAuthenticatorMixin:
    """
    This test class contains test cases for the `AbstractBasicAuthApiClient` class
    to ensure that the authentication process using Basic Auth is working correctly.
    """

    @patch("eox_nelp.api_clients.authenticators.requests.Session")
    def test_authentication_call(self, session_mock):
        """
        Test the authentication call for the API client.

        This test case ensures that the `_authenticate` method of the `AbstractBasicAuthApiClient`
        class sets the expected HTTP Basic authentication credentials (user and password)
        in the session object.

        Expected behavior:
            - Session mock is called once.
            - api client has the attribute session
            - Session has the right auth value.
        """
        expected_auth = HTTPBasicAuth(self.user, self.password)
        session_mock.return_value.auth = expected_auth

        api_client = self.api_class()

        session_mock.assert_called_once()
        self.assertEqual(api_client.session, session_mock.return_value)
        self.assertEqual(api_client.session.auth, expected_auth)
