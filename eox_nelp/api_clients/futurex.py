"""Client module for Futurex API integration.

Classes:
    FuturexApiClient: Base class to interact with Futurex services.
    FuturexMissingArguments: Exception used for indicate that some required arguments are missing.
"""
import logging

import requests
from django.conf import settings
from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from rest_framework import status

LOGGER = logging.getLogger(__name__)


class FuturexApiClient:
    """Allow to perform multiple Futurex API operations based on an authenticated session.

    Attributes:
        base_url: Futurex domain.
        session: persist certain parameters across requests.
    """

    def __init__(self):
        """FuturexApiClient creator, this will set the session based on the authenticate result"""
        self.base_url = getattr(settings, "FUTUREX_API_URL")
        client_id = getattr(settings, "FUTUREX_API_CLIENT_ID")
        client_secret = getattr(settings, "FUTUREX_API_CLIENT_SECRET")

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
            client_id<str>: Public identifier of futurex application.
            client_secret<str>: Confidential identifier used to authenticate against Futurex.

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
        """This method uses the session attribute to perform a POS request based on the
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

        return {}

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

        return {}

    def enrollment_progress(self, enrollment_data):
        """Push the user progress across for a course. This data will affect the learner profile
        in FutureX according to their progress.

        Args:
            enrollment_data<Dict>: Information about a specific progress.

        Returns:
            response<Dict>: requests response as dictionary.

        Raise:
            Basic exception when the enrollment data is not completed.
        """
        path = "enrollment-progress"
        required_fields = set([
            "courseId",
            "userId",
            "approxTotalCourseHrs",
            "overallProgress",
            "membershipState",
            "enrolledAt",
            "isCompleted",
        ])

        enrollment_data_keys = set(enrollment_data.keys())

        if required_fields <= enrollment_data_keys:
            return self.make_post(path, enrollment_data)

        raise FuturexMissingArguments(
            f"The following arguments are missing {str(required_fields - enrollment_data_keys)}",
        )


class FuturexMissingArguments(ValueError):
    """This exception indicates that one or more required arguments are missing"""
