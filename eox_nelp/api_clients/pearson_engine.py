"""Client module for Pearson Engine API integration.

Classes:
    PearsonEngineApiClient: Base class to interact with Pearson Engine services.
"""
from django.conf import settings

from eox_nelp.api_clients import AbstractAPIRestClient
from eox_nelp.api_clients.authenticators import Oauth2Authenticator


class PearsonEngineApiClient(AbstractAPIRestClient):
    """
    Client to interact with Pearson Engine API for importing candidate demographics
    and exam authorization data.

    Attributes:
        client_id (str): The client ID for Pearson Engine API.
        client_secret (str): The client secret for Pearson Engine API.
        authentication_path (str): The path for authentication.
    """
    authentication_class = Oauth2Authenticator

    def __init__(self):
        self.client_id = getattr(settings, "PEARSON_ENGINE_API_CLIENT_ID")
        self.client_secret = getattr(settings, "PEARSON_ENGINE_API_CLIENT_SECRET")
        self.authentication_path = "oauth2/token/"

        super().__init__()

    @property
    def base_url(self):
        """Return the base URL for Pearson Engine API."""
        return getattr(settings, "PEARSON_ENGINE_API_URL")

    def _get_user_data(self, user):
        """
        Retrieve user data for the request payload.

        Args:
            user: The user object containing user data.

        Returns:
            dict: The user data formatted for the request.
        """
        return {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "country": user.profile.country.code,
            "city": user.profile.city,
            "phone": user.profile.phone_number,
            "address": user.profile.mailing_address,
            "arabic_first_name": user.extrainfo.arabic_first_name,
            "arabic_last_name": user.extrainfo.arabic_last_name,
        }

    def _get_platform_data(self):
        """
        Retrieve platform data for the request payload.

        Returns:
            dict: The platform data formatted for the request.
        """
        return {
            "name": settings.PLATFORM_NAME,
            "tenant": getattr(settings, "EDNX_TENANT_DOMAIN", None)
        }

    def _get_exam_data(self, exam_id):
        """
        Retrieve exam data for the request payload.

        Args:
            exam_id: The external key for the exam.

        Returns:
            dict: The exam data formatted for the request.
        """
        return {
            "external_key": exam_id,
        }

    def import_candidate_demographics(self, user, **kwargs):
        """
        Import candidate demographics into Pearson Engine.

        Args:
            user: The user object containing user data.

        Returns:
            dict: The response from Pearson Engine API.
        """
        path = "rti/api/v1/candidate-demographics/"
        data = {
            "user_data": self._get_user_data(user),
            "platform_data": self._get_platform_data(),
            **kwargs
        }

        return self.make_post(path, data)

    def import_exam_authorization(self, user, exam_id, **kwargs):
        """
        Import exam authorization data into Pearson Engine.

        Args:
            user: The user object containing user data.
            exam_id: The external key for the exam.

        Returns:
            dict: The response from Pearson Engine API.
        """
        path = "rti/api/v1/exam-authorization/"
        data = {
            "user_data": {"username": user.username},
            "exam_data": self._get_exam_data(exam_id),
            **kwargs
        }

        return self.make_post(path, data)

    def real_time_import(self, user, exam_id, **kwargs):
        """
        Perform a real-time import of exam authorization data.

        Args:
            user: The user object containing user data.
            exam_id: The external key for the exam.

        Returns:
            dict: The response from Pearson Engine API.
        """
        path = "rti/api/v1/exam-authorization/"
        data = {
            "user_data": self._get_user_data(user),
            "exam_data": self._get_exam_data(exam_id),
            "platform_data": self._get_platform_data(),
            **kwargs
        }

        return self.make_post(path, data)
