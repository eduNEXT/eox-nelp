"""This file contains the common functions and classes for the api_clients module.

Classes:
    AbstractApiClient: Base API class.
"""
import logging
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from django.conf import settings

from eox_nelp.api_clients.authenticators import UnAuthenticatedAuthenticator

LOGGER = logging.getLogger(__name__)


class AbstractApiClient(ABC):
    """Abstract api client class, this defines common API client methods."""

    authentication_class = UnAuthenticatedAuthenticator
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

    def _authenticate(self):
        """Calls the authenticator's authenticate method"""
        authenticator = self.authentication_class()

        return authenticator.authenticate(api_client=self)

    def _get_extra_headers(self):
        """This verify the extra_headers_key attribute and returns its value from the django settings.

        Returns
            Dict: The extra_headers_key must be set a dictionary.
        """
        if self.extra_headers_key:
            return getattr(settings, self.extra_headers_key, {})

        return {}


class AbstractAPIRestClient(AbstractApiClient):
    """This abstract class is an extension of AbstractApiClient that includes common http methods (POST and  GET)
    based on the REST API standard.
    """

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


class AbstractSOAPClient(AbstractApiClient):
    """This abstract class is an extension of AbstractApiClient that includes
    a common POST method whose expected result is a xml response.
    """

    def make_post(self, path, data):
        """This method uses the session attribute to perform a POST request based on the
        base_url attribute and the given path, if the status code is different from 200 this
        will log the error and finally this will return the xml response in any case.

        Arguments:
            path <str>: makes reference to the url path.
            data <str>: request body as xml string.

        Return:
            BeautifulSoup: xml response.
        """
        url = f"{self.base_url}/{path}"

        response = self.session.post(url=url, data=data)
        content = response.text

        if not response.ok:
            LOGGER.error(
                "An error has occurred trying to make post request to %s with status code %s and message %s",
                url,
                response.status_code,
                content,
            )

        return BeautifulSoup(content, "xml")
