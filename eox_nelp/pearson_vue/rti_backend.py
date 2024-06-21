"""
This module provides the RealTimeImport class, which is responsible for orchestrating the RTI pipeline
and executing various processes related to rti.

Classes:
    RealTimeImport: Class for managing RTI operations and executing the pipeline.
"""
import importlib

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
from eox_nelp.utils import remove_keys_from_dict


class RealTimeImport:
    """
    Class for managing RTI (Real Time Import) operations and executing the pipeline.

    Attributes:
        backend_data (dict): A dictionary containing backend-specific data.

    Methods:
        run_pipeline(): Executes the RTI pipeline by iterating through the pipeline functions.
        get_pipeline(): Returns the RTI pipeline, which is a list of functions to be executed.
    """

    def __init__(self, **kwargs):
        """
        Initializes the RealTimeImport instance with the provided keyword arguments.

        Args:
            **kwargs: Additional keyword arguments to configure the RealTimeImport instance.
        """
        self.backend_data = kwargs.copy()

    def run_pipeline(self):
        """
        Executes the RTI pipeline by iterating through the pipeline functions.
        """
        pipeline = self.get_pipeline()
        pipeline_index = self.backend_data.get("pipeline_index", 0)

        for idx, func in enumerate(pipeline[pipeline_index:]):
            self.backend_data["pipeline_index"] = pipeline_index + idx
            try:
                result = func(**self.backend_data) or {}
            except PearsonBaseError as pearson_error:
                self.backend_data["pipeline_index"] = len(pipeline) - 1
                # clean kwargs to dont finish next pipeline launch.
                executed__pipeline_kwargs = remove_keys_from_dict(self.backend_data, ["pipeline_index"])
                executed__pipeline_kwargs["failed_step_pipeline"] = func.__name__
                tasks = importlib.import_module("eox_nelp.pearson_vue.tasks")
                tasks.rti_error_handler_task.delay(**executed__pipeline_kwargs, **pearson_error.__dict__)
                break

            self.backend_data.update(result)
            if result.get("safely_pipeline_termination"):
                self.backend_data["pipeline_index"] = len(pipeline) - 1
                break

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


class ErrorRealTimeImportHandler(RealTimeImport):
    """Class for managing validation error pipe  executing the pipeline for data validation."""
    def get_pipeline(self):
        """
        Returns the error validation pipeline, which is a list of functions to be executed.
        """
        return [
            audit_pearson_error,
        ]
