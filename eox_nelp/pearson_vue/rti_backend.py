"""
This module provides the RealTimeImport class, which is responsible for orchestrating the RTI pipeline
and executing various processes related to rti.

Classes:
    RealTimeImport: Class for managing RTI operations and executing the pipeline.
"""
import importlib
from abc import ABC, abstractmethod

from eox_nelp.pearson_vue.exceptions import PearsonBaseError
from eox_nelp.pearson_vue.pipeline import (
    audit_pearson_error,
    build_cdd_request,
    build_ead_request,
    check_service_availability,
    get_exam_data,
    get_user_data,
    handle_course_completion_status,
    import_candidate_demographics,
    import_exam_authorization,
    validate_cdd_request,
    validate_ead_request,
)


class AbstractBackend(ABC):
    """
    Base class for managing backend operations and executing pipelines.

    This class provides the core functionality to manage backend data and run a sequence of operations,
    defined as a pipeline, to process the data. Subclasses must override the `get_pipeline` method
    to provide specific pipeline functions.

    Attributes:
        backend_data (dict): A dictionary containing backend-specific data.

    Methods:
        run_pipeline(): Executes the pipeline by iterating through the pipeline functions.
        get_pipeline(): Returns the pipeline, which is a list of functions to be executed (abstract method).
        handle_error(exception: Exception, failed_step_pipeline: str): Handles errors during pipeline execution.
    """

    def __init__(self, **kwargs):
        """
        Initializes the AbstractBackend instance with the provided keyword arguments.

        Args:
            **kwargs: Additional keyword arguments to configure the AbstractBackend instance.
        """
        self.backend_data = kwargs.copy()

    def run_pipeline(self):
        """
        Executes the pipeline by iterating through the pipeline functions.

        This method retrieves the pipeline using the `get_pipeline` method and executes each function
        in the pipeline sequentially. If an error occurs during the execution of a function, it calls
        `handle_error` method to handle the error and stops the pipeline execution.
        """
        pipeline = self.get_pipeline()
        pipeline_index = self.backend_data.get("pipeline_index", 0)

        for idx, func in enumerate(pipeline[pipeline_index:]):
            self.backend_data["pipeline_index"] = pipeline_index + idx
            try:
                result = func(**self.backend_data) or {}
            except PearsonBaseError as pearson_error:
                self.handle_error(pearson_error, func.__name__)
                break

            self.backend_data.update(result)
            if result.get("safely_pipeline_termination"):
                self.backend_data["pipeline_index"] = len(pipeline) - 1
                break

    @abstractmethod
    def get_pipeline(self):
        """
        Returns the pipeline, which is a list of functions to be executed.

        Subclasses must override this method to provide the specific functions to be executed in the pipeline.

        Returns:
            list: A list of functions representing the pipeline.
        """

    @abstractmethod
    def handle_error(self, exception, failed_step_pipeline):
        """
        Handles errors during pipeline execution.

        Args:
            exception (PearsonBaseError): The exception that was raised.
            failed_step_pipeline (str): The name of the pipeline step where the error occurred.
        """


class ErrorRealTimeImportHandler(AbstractBackend):
    """Class for managing validation error pipe  executing the pipeline for data validation."""

    def handle_error(self, exception, failed_step_pipeline):
        """
        Handles errors during pipeline execution.

        Args:
            exception (Exception): The exception that was raised.
            failed_step_pipeline (str): The name of the pipeline step where the error occurred.
        """

    def get_pipeline(self):
        """
        Returns the error validation pipeline, which is a list of functions to be executed.
        """
        return [
            audit_pearson_error,
        ]


class RealTimeImport(AbstractBackend):
    """
    Class for managing RTI (Real Time Import) operations and executing the pipeline.

    Attributes:
        backend_data (dict): A dictionary containing backend-specific data.

    Methods:
        run_pipeline(): Executes the RTI pipeline by iterating through the pipeline functions.
        get_pipeline(): Returns the RTI pipeline, which is a list of functions to be executed.
    """

    def handle_error(self, exception, failed_step_pipeline):
        """
        Handles errors during pipeline execution.

        Args:
            exception (Exception): The exception that was raised.
            failed_step_pipeline (str): The name of the pipeline step where the error occurred.
        """
        tasks = importlib.import_module("eox_nelp.pearson_vue.tasks")
        tasks.rti_error_handler_task.delay(
            failed_step_pipeline=failed_step_pipeline,
            exception_dict=exception.to_dict(),
            course_id=self.backend_data.get("course_id"),
            user_id=self.backend_data.get("user_id"),
        )

    def get_pipeline(self):
        """
        Returns the RTI pipeline, which is a list of functions to be executed.
        """
        return [
            handle_course_completion_status,
            get_user_data,
            get_exam_data,
            build_cdd_request,
            validate_cdd_request,
            build_ead_request,
            validate_ead_request,
            check_service_availability,
            import_candidate_demographics,
            import_exam_authorization,
        ]


class ExamAuthorizationDataImport(RealTimeImport):
    """Class for EAD requests (Exam Authorization Data operations) and executing the pipeline."""

    def get_pipeline(self):
        """
        Returns the EAD pipeline, which is a list of functions to be executed.
        """
        return [
            get_user_data,
            get_exam_data,
            build_ead_request,
            validate_ead_request,
            check_service_availability,
            import_exam_authorization,
        ]


class CandidateDemographicsDataImport(RealTimeImport):
    """Class for CDD requests (Candidate Demographics Data operations) and executing the pipeline."""

    def get_pipeline(self):
        """
        Returns the CDD pipeline, which is a list of functions to be executed.
        """
        return [
            get_user_data,
            build_cdd_request,
            validate_cdd_request,
            check_service_availability,
            import_candidate_demographics,
        ]
