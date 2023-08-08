"""Client module for Futurex API integration.

Classes:
    FuturexApiClient: Base class to interact with Futurex services.
    FuturexMissingArguments: Exception used for indicate that some required arguments are missing.
"""
from django.conf import settings

from eox_nelp.api_clients import AbstractOauth2ApiClient


class FuturexApiClient(AbstractOauth2ApiClient):
    """Allow to perform multiple Futurex API operations based on an authenticated session.

    Attributes:
        base_url: Futurex domain.
        session: persist certain parameters across requests.
    """
    @property
    def base_url(self):
        return getattr(settings, "FUTUREX_API_URL")

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
