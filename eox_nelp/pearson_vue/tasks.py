"""
This module contains functions and classes for making asynchronous calls to Pearson VUE's RTI services.

Functions:
    real_time_import_task(data: dict) -> None: Performs an asynchronous call to the RTI service.
"""

from celery import shared_task

from eox_nelp.pearson_vue.rti_backend import (
    CandidateDemographicsDataImport,
    ErrorValidationDataImport,
    ExamAuthorizationDataImport,
    RealTimeImport,
)


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
def error_validation_task(self, pipeline_index=0, **kwargs):
    """
    Performs an asynchronous call to manage Pearson validation error task.

    This task initiates the real-time import process using the provided pipeline index and optional keyword arguments.

    Args:
        self: The Celery task instance.
        pipeline_index (int): The index of the pipeline to be executed (default is 0).
        **kwargs: Additional keyword arguments to configure the RTI service.
    """
    error_validation = ErrorValidationDataImport(pipeline_index=pipeline_index, **kwargs.copy())

    try:
        error_validation.run_pipeline()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        self.retry(exc=exc, kwargs=error_validation.backend_data)
