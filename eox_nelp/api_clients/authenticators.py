"""
This module contains classes for authenticating users using various authentication methods.

Classes:
    BasicAuthenticator:
        A class for authenticating users using Basic Authentication with a username and password.

    Oauth2Authenticator:
        A class for authenticating users using OAuth 2.0 with client ID and client secret.

    UnAuthenticatedAuthenticator:
        A class for unauthenticated request.
"""
from abc import ABC, abstractmethod

import requests
from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session


class AbstractAuthenticator(ABC):
    """This class define required methods that an autheticator class must have."""

    @abstractmethod
    def authenticate(self, api_client):
        """Abstract method that should return a requests Session."""
        raise NotImplementedError


class Oauth2Authenticator(AbstractAuthenticator):
    """ Oauth2Authenticator is a class for authenticating users using
    the OAuth 2.0 standard with client ID and client secret.
    """

    def authenticate(self, api_client):
        """Authenticate the session with OAuth 2.0 credentials.

        This method uses OAuth 2.0 client credentials (client ID and client secret)
        to obtain an access token from the OAuth token endpoint. The access token
        is then used to create and configure a requests session.

        The access token is cached to minimize token requests to the OAuth server.

        Returns:
            requests.Session: Session authenticated with OAuth 2.0 credentials.
        """
        # pylint: disable=no-member
        key = f"{api_client.client_id}-{api_client.client_secret}"
        headers = cache.get(key)

        if not headers:
            client = BackendApplicationClient(client_id=api_client.client_id)
            oauth = OAuth2Session(client_id=api_client.client_id, client=client)
            authenticate_url = f"{api_client.base_url}/oauth/token"
            response = oauth.fetch_token(
                token_url=authenticate_url,
                client_secret=api_client.client_secret,
                include_client_id=True,
            )
            headers = {
                "Authorization": f"{response.get('token_type')} {response.get('access_token')}"
            }

            cache.set(key, headers, response.get("expires_in", 300))

        session = requests.Session()
        session.headers.update(headers)

        return session


class BasicAuthAuthenticator(AbstractAuthenticator):
    """ BasicAuthenticator is a class for authenticating users
    using Basic Authentication with a username and password.
    """

    def authenticate(self, api_client):
        """Authenticate the session with the user and password.

        Creates and configures a requests session with basic authentication
        provided by the user and password.

        Returns:
            requests.Session: Session authenticated.
        """
        # pylint: disable=no-member
        session = requests.Session()
        session.auth = HTTPBasicAuth(api_client.user, api_client.password)

        return session


class UnAuthenticatedAuthenticator(AbstractAuthenticator):
    """This authenticator class doesn't implement any authentication method."""

    def authenticate(self, api_client):
        """Creates and configures a requests session without authentication.

        Returns:
            requests.Session: Basic Session.
        """
        # pylint: disable=no-member
        return requests.Session()
