"""Client module for minister of tourism API integration.

Classes:
    MinisterOfTourismApiClient: Class to interact with Minister of tourism external service.
"""
from django.conf import settings

from eox_nelp.api_clients import AbstractAPIRestClient
from eox_nelp.api_clients.authenticators import BasicAuthAuthenticator

try:
    from eox_audit_model.decorators import audit_method
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x


class MinisterOfTourismApiClient(AbstractAPIRestClient):
    """Allow to perform multiple external certificates operations."""

    authentication_class = BasicAuthAuthenticator

    def __init__(self):
        self.user = getattr(settings, "MINISTER_OF_TOURISM_USER")
        self.password = getattr(settings, "MINISTER_OF_TOURISM_PASSWORD")

        super().__init__()

    @property
    def base_url(self):
        return getattr(settings, "MINISTER_OF_TOURISM_API_URL")

    def update_training_stage(self, course_id, national_id, stage_result):
        """This updates the training stage, changes the status to pass or fail, and stores them in HCD
        database. If the training stage is already updated or some parameters are missing or wrong, an error
        message is returned.

        Arguments:
            course_id<str>: Course identifier as string, e.g, course-v1:edx+cos104+T4_2023
            national_id<str>: User national identifier, e.g. 1087583085
            stage_result<int>: Representation of pass or fail result, 1 for pass 2 for fail.

        Returns:
            response<Dict>: requests response as dictionary.
        """
        @audit_method(action="Publish MT course completion stage")
        def update_training_stage_request(course_id, national_id, stage_result):
            """This is a wrapper that allows to make audit-able the update_training_stage method."""
            path = "api/v2/LMSCourse/UpdateTrainingStage"
            payload = {
                "courseLMSId": course_id,
                "userNationalId": national_id,
                "applicationStageResult": stage_result,
            }
            return self.make_post(path, payload)

        return update_training_stage_request(course_id, national_id, stage_result)
