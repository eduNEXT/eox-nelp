"""
This module provides the RealTimeImport class, which is responsible for orchestrating the RTI pipeline
and executing various processes related to rti.

Classes:
    RealTimeImport: Class for managing RTI operations and executing the pipeline.
"""
from eox_nelp.pearson_vue.pipeline import (
    check_service_availability,
    get_exam_data,
    get_user_data,
    handle_course_completion_status,
    import_candidate_demographics,
    import_exam_authorization,
)


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
            result = func(**self.backend_data) or {}
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
            check_service_availability,
            import_candidate_demographics,
            import_exam_authorization,
        ]
