"""
This module contains classes for authenticating users using various authentication methods.

Classes:
    BasicAuthenticator:
        A class for authenticating users using Basic Authentication with a username and password.

    Oauth2Authenticator:
        A class for authenticating users using OAuth 2.0 with client ID and client secret.

    UnAuthenticatedAuthenticator:
        A class for unauthenticated request.

    PKCS12Authenticator:
        A class for authenticating users using PFX certificate.
"""
from abc import ABC, abstractmethod

import requests
from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from requests_pkcs12 import Pkcs12Adapter


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
            authenticate_url = f"{api_client.base_url}/{api_client.authentication_path}"
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


class PKCS12Authenticator(AbstractAuthenticator):
    """PKCS12Authenticator is a class for authenticating users
    using a PFX certificate and its passphrase.
    """

    def authenticate(self, api_client):
        """Creates and configures a requests session with a specific certificate.

        Returns:
            requests.Session: Basic Session.
        """
        session = requests.Session()
        session.mount(
            api_client.base_url,
            Pkcs12Adapter(pkcs12_filename=api_client.cert, pkcs12_password=api_client.passphrase),
        )

        return session


class Oauth2BasicAuthenticator(BasicAuthAuthenticator):
    """Authenticator for custom use using basic auth to get a Oauth2 Token (Bearer or JWT).
    Token_type on depends of the response used after the oauth2 token request.
    Then the token is used for the next requests.
    """

    def authenticate(self, api_client):
        """Authenticate the session with basic auth in order to get token(Bearer or JWT).
        Then the token is added to a new session Headers.
        Is needed the user, password and token_path class atrributes to the get oauth2 token,
        based on the client configuration.
        """
        auth_session = super().authenticate(api_client)
        key = f"oauth2-basic-{api_client.user}-{api_client.password}"
        headers = cache.get(key)

        if not headers:
            authenticate_url = f"{api_client.base_url}/{api_client.token_path}"
            response = auth_session.post(
                url=authenticate_url,
                data={"grant_type": "client_credentials", "scope": "notification"}
            ).json()
            headers = {
                "Authorization": f"{response.get('token_type')} {response.get('access_token')}"
            }

            cache.set(key, headers, int(response.get("expires_in", 300)))

        session = requests.Session()
        session.headers.update(headers)

        return session
