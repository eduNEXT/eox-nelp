"""This file contains the common functions and classes for the api_clients module.

Classes:
    AbstractApiClient: Base API class.
"""
import logging
from abc import ABC, abstractmethod

import requests
from django.conf import settings
from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

LOGGER = logging.getLogger(__name__)


class AbstractApiClient(ABC):
    """Abstract api client class, this implement a basic authentication method and defines methods POST and GET"""

    extra_headers_key = None

    @property
    @abstractmethod
    def base_url(self):
        """Abstract base_url property method."""
        raise NotImplementedError

    def __init__(self):
        """
        Abstract ApiClient creator, this will set the session based on the authenticate result.
        """
        self.session = self._authenticate()
        self.session.headers.update(self._get_extra_headers())

    @abstractmethod
    def _authenticate(self):
        """Abstract method that should return a requests Session instance in its implementation."""
        raise NotImplementedError

    def _get_extra_headers(self):
        """This verify the extra_headers_key attribute and returns its value from the django settings.

        Returns
            Dict: The extra_headers_key must be set a dictionary.
        """
        if self.extra_headers_key:
            return getattr(settings, self.extra_headers_key, {})

        return {}

    def make_post(self, path, data):
        """This method uses the session attribute to perform a POST request based on the
        base_url attribute and the given path, if the response has a status code 200
        this will return the json from that response otherwise this will return an empty dictionary.

        Args:
            path<str>: makes reference to the url path.
            data<Dict>: request body as dictionary.

        Return:
            Dictionary: Empty dictionary or json response.
        """
        url = f"{self.base_url}/{path}"

        response = self.session.post(url=url, json=data)

        if response.ok:
            return response.json()

        LOGGER.error(
            "An error has occurred trying to make post request to %s with status code %s and message %s",
            url,
            response.status_code,
            response.json(),
        )

        return {
            "error": True,
            "message": f"Invalid response with status {response.status_code}"
        }

    def make_get(self, path, payload):
        """This method uses the session attribute to perform a GET request based on the
        base_url attribute and the given path, if the response has a status code 200
        this will return the json from that response otherwise this will return an empty dictionary.

        Args:
            path<str>: makes reference to the url path.
            payload<Dict>: queryparams as dictionary.

        Return:
            Dictionary: Empty dictionary or json response.
        """
        url = f"{self.base_url}/{path}"

        response = self.session.get(url=url, params=payload)

        if response.ok:
            return response.json()

        LOGGER.error(
            "An error has occurred trying to make a get request to %s with status code %s and message %s",
            url,
            response.status_code,
            response.json(),
        )

        return {
            "error": True,
            "message": f"Invalid response with status {response.status_code}"
        }


class AbstractOauth2ApiClient(AbstractApiClient):
    """Abstract class for an OAuth 2.0 authentication API client.

    This class provides basic functionality for an API client that requires
    OAuth 2.0 authentication using the client ID and client secret.

    Attributes:
        client_id (str): Client ID for OAuth 2.0 authentication.
        client_secret (str): Client secret for OAuth 2.0 authentication.
    """

    def _authenticate(self):
        """Authenticate the session with OAuth 2.0 credentials.

        This method uses OAuth 2.0 client credentials (client ID and client secret)
        to obtain an access token from the OAuth token endpoint. The access token
        is then used to create and configure a requests session.

        The access token is cached to minimize token requests to the OAuth server.

        Returns:
            requests.Session: Session authenticated with OAuth 2.0 credentials.
        """
        # pylint: disable=no-member
        key = f"{self.client_id}-{self.client_secret}"
        headers = cache.get(key)

        if not headers:
            client = BackendApplicationClient(client_id=self.client_id)
            oauth = OAuth2Session(client_id=self.client_id, client=client)
            authenticate_url = f"{self.base_url}/oauth/token"
            response = oauth.fetch_token(
                token_url=authenticate_url,
                client_secret=self.client_secret,
                include_client_id=True,
            )
            headers = {
                "Authorization": f"{response.get('token_type')} {response.get('access_token')}"
            }

            cache.set(key, headers, response.get("expires_in", 300))

        session = requests.Session()
        session.headers.update(headers)

        return session


class AbstractBasicAuthApiClient(AbstractApiClient):
    """Abstract class for a basic authentication API client.

    This class provides basic functionality for an API client that requires
    basic authentication using a usern and password.

    Attributes:
        user (str): Username for basic authentication.
        password (str): Password for basic authentication.
    """

    def _authenticate(self):
        """Authenticate the session with the user and password.

        Creates and configures a requests session with basic authentication
        provided by the user and password.

        Returns:
            requests.Session: Session authenticated.
        """
        # pylint: disable=no-member
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.user, self.password)

        return session


class AbstractBasicApiClient(AbstractApiClient):
    """Abstract class for a basic  API client without authentication.
    This class provides basic functionality for an API client that requires
    basic api client without auth. Use a normal session.
    """
    def _authenticate(self):
        """Creates and configures a requests session without authentication.

        Returns:
            requests.Session: Basic Session.
        """
        # pylint: disable=no-member
        return requests.Session()
