"""
This module contains functions and classes for making asynchronous calls to Pearson VUE's RTI services.

Functions:
    real_time_import_task(data: dict) -> None: Performs an asynchronous call to the RTI service.
"""
from celery import shared_task
from django.contrib.auth import get_user_model
from nelc_api_clients.clients.pearson_engine import PearsonEngineApiClient
from requests import exceptions

from eox_nelp.pearson_vue.constants import ALLOWED_RTI_ACTIONS
from eox_nelp.pearson_vue.pipeline import audit_method, rename_function
from eox_nelp.pearson_vue.rti_backend import (
    CandidateDemographicsDataImport,
    ErrorRealTimeImportHandler,
    ExamAuthorizationDataImport,
    RealTimeImport,
)
from eox_nelp.pearson_vue.utils import generate_action_parameters, update_user_engines

User = get_user_model()


@shared_task(bind=True)
def real_time_import_task(self, pipeline_index=0, **kwargs):
    """
    Performs an asynchronous call to Pearson VUE's RTI (Real Time Import) service.

    This task initiates the real-time import process using the provided pipeline index and optional keyword arguments.

    Args:
        self: The Celery task instance.
        pipeline_index (int): The index of the pipeline to be executed (default is 0).
        **kwargs: Additional keyword arguments to configure the RTI service.
    """
    rti = RealTimeImport(pipeline_index=pipeline_index, **kwargs.copy())

    try:
        rti.run_pipeline()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        self.retry(exc=exc, kwargs=rti.backend_data)


@shared_task(bind=True)
def ead_task(self, pipeline_index=0, **kwargs):
    """
    Performs an asynchronous call to Pearson VUE's EAD task (Exam Authorization Data) service.

    This task initiates the real-time import process using the provided pipeline index and optional keyword arguments.

    Args:
        self: The Celery task instance.
        pipeline_index (int): The index of the pipeline to be executed (default is 0).
        **kwargs: Additional keyword arguments to configure the RTI service.
    """
    ead = ExamAuthorizationDataImport(pipeline_index=pipeline_index, **kwargs.copy())

    try:
        ead.run_pipeline()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        self.retry(exc=exc, kwargs=ead.backend_data)


@shared_task(bind=True)
def cdd_task(self, pipeline_index=0, **kwargs):
    """
    Performs an asynchronous call to Pearson VUE's CDD task (Candidate Demographics Data) service.

    This task initiates the real-time import process using the provided pipeline index and optional keyword arguments.

    Args:
        self: The Celery task instance.
        pipeline_index (int): The index of the pipeline to be executed (default is 0).
        **kwargs: Additional keyword arguments to configure the RTI service.
    """
    cdd = CandidateDemographicsDataImport(pipeline_index=pipeline_index, **kwargs.copy())

    try:
        cdd.run_pipeline()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        self.retry(exc=exc, kwargs=cdd.backend_data)


@shared_task(bind=True)
def rti_error_handler_task(self, pipeline_index=0, **kwargs):
    """
    Performs an asynchronous call to manage Pearson validation error task.

    This task initiates the real-time import process using the provided pipeline index and optional keyword arguments.

    Args:
        self: The Celery task instance.
        pipeline_index (int): The index of the pipeline to be executed (default is 0).
        **kwargs: Additional keyword arguments to configure the RTI service.
    """
    error_rti = ErrorRealTimeImportHandler(pipeline_index=pipeline_index, **kwargs.copy())

    try:
        error_rti.run_pipeline()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        self.retry(exc=exc, kwargs=error_rti.backend_data)


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
        action = getattr(PearsonEngineApiClient(), action_key)
        parameters = generate_action_parameters(user, exam_id)
        response = action(**parameters, **kwargs)

        if response.get("error"):
            raise Exception(response.get("message", "Unknown error"))  # pylint: disable=broad-exception-raised

    audit_pearson_engine_action(user_id, exam_id, action_key, **kwargs)
