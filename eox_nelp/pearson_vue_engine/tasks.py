"""
This module contains functions and classes for making asynchronous calls to Pearson VUE's RTI services.

Tasks:
    real_time_import_task_v2(user_id: int, exam_id: str, action_name: str, **kwargs) -> None:
        Performs an asynchronous call to the Pearson Engine API to execute a real-time import action.
"""
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from nelc_api_clients.clients.pearson_engine import PearsonEngineApiClient
from requests import exceptions

from eox_nelp.pearson_vue_engine.constants import ALLOWED_RTI_ACTIONS
from eox_nelp.pearson_vue_engine.utils import generate_action_parameters, update_user_engines

try:
    from eox_audit_model.decorators import audit_method, rename_function
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x

    def rename_function(name):  # pylint: disable=unused-argument
        """Identity rename_function"""
        return lambda x: x

User = get_user_model()


@shared_task(autoretry_for=(exceptions.Timeout, exceptions.ConnectionError), retry_backoff=5)
def real_time_import_task_v2(user_id, exam_id=None, action_name="rti", **kwargs):
    """
    Asynchronous task to perform a real-time import action using the Pearson Engine API.

    This task handles different types of import actions, such as real-time import,
    importing candidate demographics, and importing exam authorizations, by calling
    the appropriate method on the PearsonEngineApiClient.

    Args:
        user_id (int): The ID of the user to be processed.
        exam_id (str, optional): The ID of the exam for authorization. Default is None.
        action_name (str, optional): The action to perform. Default is "rti".
            Supported actions are:
                - "rti" for real_time_import
                - "cdd" for import_candidate_demographics
                - "ead" for import_exam_authorization
        **kwargs: Additional keyword arguments to pass to the API client method.

    Raises:
        KeyError: If action_name is not found in ALLOWED_RTI_ACTIONS.
        User.DoesNotExist: If the user with the given user_id does not exist.
    """
    action_key = ALLOWED_RTI_ACTIONS[action_name]

    @audit_method(action="Pearson Engine Action")
    @rename_function(name=action_key)
    def audit_pearson_engine_action(user_id, exam_id, action_key, **kwargs):
        user = User.objects.get(id=user_id)
        update_user_engines(user, action_name, exam_id)
        client = PearsonEngineApiClient(
            client_id=settings.PEARSON_ENGINE_API_CLIENT_ID,
            client_secret=settings.PEARSON_ENGINE_API_CLIENT_SECRET,
            base_url=settings.PEARSON_ENGINE_API_URL,
        )
        action = getattr(client, action_key)
        parameters = generate_action_parameters(user, exam_id)
        response = action(**parameters, **kwargs)

        if response.get("error"):
            raise Exception(response.get("message", "Unknown error"))  # pylint: disable=broad-exception-raised

    audit_pearson_engine_action(user_id, exam_id, action_key, **kwargs)
