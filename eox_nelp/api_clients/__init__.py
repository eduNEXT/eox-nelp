"""This file contains the common functions and classes for the api_clients module.

Classes:
    AbstractApiClient: Base API class.
"""
import logging
from abc import ABC, abstractmethod

import requests
from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from rest_framework import status

LOGGER = logging.getLogger(__name__)


class AbstractApiClient(ABC):
    """Abstract api client class, this implement a basic authentication method and defines methods POST and GET"""

    @property
    @abstractmethod
    def base_url(self):
        """Abstract base_url property method."""
        raise NotImplementedError

    def __init__(self, client_id, client_secret):
        """
        Abstract ApiClient creator, this will set the session based on the authenticate result.

        Args:
            client_id<str>: Public application identifier.
            client_secret<str>: Confidential identifier.
        """
        key = f"{client_id}-{client_secret}"
        headers = cache.get(key)

        if not headers:
            response = self._authenticate(client_id, client_secret)
            headers = {
                "Authorization": f"{response.get('token_type')} {response.get('access_token')}"
            }

            cache.set(key, headers, response.get("expires_in", 300))

        self.session = requests.Session()
        self.session.headers.update(headers)

    def _authenticate(self, client_id, client_secret):
        """This method uses the session attribute to perform a POS request based on the
        base_url attribute and the given path, if the response has a status code 200
        this will return the json from that response otherwise this will return an empty dictionary.

        Args:
            client_id<str>: Public application identifier.
            client_secret<str>: Confidential identifier.

        Return:
            Dictionary: Response from authentication request.
        """
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client_id=client_id, client=client)
        authenticate_url = f"{self.base_url}/oauth/token"

        return oauth.fetch_token(
            token_url=authenticate_url,
            client_secret=client_secret,
            include_client_id=True,
        )

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

        if response.status_code == status.HTTP_200_OK:
            return response.json()

        LOGGER.error(
            "An error has occurred trying to make post request to %s with status code %s",
            url,
            response.status_code,
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

        if response.status_code == status.HTTP_200_OK:
            return response.json()

        LOGGER.error(
            "An error has occurred trying to make a get request to %s with status code %s",
            url,
            response.status_code,
        )

        return {
            "error": True,
            "message": f"Invalid response with status {response.status_code}"
        }
