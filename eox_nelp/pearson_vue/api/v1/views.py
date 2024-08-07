"""
Views for handling Pearson VUE request.

This module defines views for handling various types of request in the Pearson VUE service.

Classes:
    PearsonRTENBaseView: A base view class for creating Pearson VUE RTEN events.
    ResultNotificationView: A view for handling result notification events.
    PlaceHoldView: A view for handling place hold events.
    ReleaseHoldView: A view for handling release hold events.
    ModifyResultStatusView: A view for handling modify result status events.
    RevokeResultView: A view for handling revoke result events.
    UnrevokeResultView: A view for handling unrevoke result events.
    ModifyAppointmentView: A view for handling Modify Appoinments  events.
    CancelAppointmentView: A view for handling Cancel Appoinments events.
"""
from django.conf import settings
from django.http import Http404
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from eox_core.edxapp_wrapper.bearer_authentication import BearerAuthentication
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from eox_nelp.edxapp_wrapper.student import AnonymousUserId
from eox_nelp.pearson_vue.api.v1.serializers import PearsonRTENSerializer
from eox_nelp.pearson_vue.constants import (
    CANCEL_APPOINTMENT,
    MODIFY_APPOINTMENT,
    MODIFY_RESULT_STATUS,
    PLACE_HOLD,
    RELEASE_HOLD,
    RESULT_NOTIFICATION,
    REVOKE_RESULT,
    UNREVOKE_RESULT,
)
from eox_nelp.pearson_vue.models import PearsonRTENEvent
from eox_nelp.pearson_vue.pipeline import get_enrollment_from_id
from eox_nelp.pearson_vue.rti_backend import ResultNotificationBackend


class PearsonRTENBaseView(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    Base view for Pearson RTEN (Real Time Event Notification) API endpoints.

    This view provides the base functionality for creating Pearson RTEN events.
    Subclasses should define the `event_type` attribute to specify the type of event.

    Attributes:
        permission_classes (list): List of permission classes required for the view.
        serializer_class (Serializer): Serializer class used for validating and parsing data.
        queryset (QuerySet): Queryset representing the model instances to operate on.
        authentication_classes (list): List of authentication classes used for authentication.
    """
    event_type = None
    permission_classes = [IsAuthenticated]
    serializer_class = PearsonRTENSerializer
    queryset = PearsonRTENEvent.objects.all()  # pylint: disable=no-member
    authentication_classes = [BearerAuthentication, JwtAuthentication]
    filter_backends = [SearchFilter]
    search_fields = ["candidate__username", "course__id"]

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch method to check if specific PEARSON_RTEN_API settings are active.

        This method checks the PEARSON_RTEN_API_WRITE_ENABLED and PEARSON_RTEN_API_READ_ENABLED
        settings based on the request method. If neither setting is active for the corresponding
        request method, it raises an Http404 exception, resulting in a 404 Not Found response.
        If the appropriate setting is active, it proceeds with the normal dispatch process.

        Args:
            request (Request): The request object containing the data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: Parent dispatch result.

        Raises:
            Http404: If neither the PEARSON_RTEN_API_WRITE_ENABLED nor the PEARSON_RTEN_API_READ_ENABLED
            setting is active for the corresponding request method.
        """
        if not self.is_api_enabled(request):
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def is_api_enabled(self, request):
        """
        Check if the Pearson RTEN API is enabled based on the request method and relevant settings.

        This method verifies the following settings:
        - PEARSON_RTEN_API_WRITE_ENABLED: If set to True and the request method is POST, the API is enabled.
        - PEARSON_RTEN_API_READ_ENABLED: If set to True and the request method is GET, the API is enabled.

        Args:
            request (Request): The request object containing the data.

        Returns:
            bool: True if the API is enabled based on the settings and request method, False otherwise.
        """
        if getattr(settings, "PEARSON_RTEN_API_WRITE_ENABLED", False) and request.method == "POST":
            return True

        if getattr(settings, "PEARSON_RTEN_API_READ_ENABLED", False) and request.method == "GET":
            return True

        return False

    def get_queryset(self):
        """
        Get the queryset for the view.

        This method filters the queryset to return only the events that match the specified event_type.

        Returns:
            QuerySet: The filtered queryset.
        """
        return PearsonRTENEvent.objects.filter(event_type=self.event_type)  # pylint: disable=no-member

    def perform_create(self, serializer):
        """
        Perform creation of Pearson RTEN event.

        This method is called when creating a new Pearson RTEN event.
        It extracts the content data from the request and saves the event using the provided serializer.

        Args:
            serializer (Serializer): The serializer instance used for data validation and saving.
        """
        content_data = self.request.data.copy()
        serializer.save(
            event_type=self.event_type,
            candidate=self.get_candidate(),
            content=content_data,
            course=self.get_course(),
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new Pearson RTEN event.

        Overrides the default create method to return a response with status code 201
        and an empty dictionary.

        Args:
            request (Request): The request object containing the data.

        Returns:
            Response: Response object with status code 201 and an empty dictionary.
        """
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            return Response({}, status=status.HTTP_200_OK, headers=response.headers)

        return response

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of objects if the user has the necessary permissions.

        This method overrides the default list method to add a permission check.
        Only users who are superusers or staff members are allowed to retrieve the list of objects.
        If the user does not have the necessary permissions, an HTTP 404 error is raised.

        Args:
            request (HttpRequest): The request object containing user information.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The response object containing the list of objects if the user has the necessary permissions.

        Raises:
            Http404: If the user does not have the necessary permissions.
        """
        if request.user.is_superuser or request.user.is_staff:
            return super().list(request, *args, **kwargs)

        raise Http404

    def get_candidate(self):
        """
        Retrieves the candidate user based on the client candidate ID provided in the request data.

        This method extracts the `clientCandidateID` from the request data, removes the "NELC" prefix,
        and attempts to retrieve the corresponding user from the `AnonymousUserId` model. If the candidate
        ID does not exist, it returns `None`.

        Returns:
            user (object or None): The user object associated with the anonymous user ID, or `None` if not found.
        """
        anonymous_user_id = self.request.data.get("clientCandidateID", "").replace("NELC", "")

        try:
            return AnonymousUserId.objects.get(anonymous_user_id=anonymous_user_id).user
        except AnonymousUserId.DoesNotExist:
            return None

    def get_course(self):
        """
        Retrieves the course associated with the enrollment ID from the request data.

        This method extracts the `clientAuthorizationID` from the request data. If the ID is present,
        it splits the ID to obtain the `enrollment_id` and then retrieves the enrollment object using
        the `get_enrollment_from_id` function. If the enrollment object exists, it returns the associated course.
        Otherwise, it returns `None`.

        Returns:
            Course or None: The course associated with the enrollment if it exists, otherwise `None`.
        """
        client_authorization_id = self.request.data.get("authorization", {}).get("clientAuthorizationID")

        if not client_authorization_id:
            return None

        enrollment_id = client_authorization_id.split("-")[0]
        enrollment = get_enrollment_from_id(enrollment_id).get("enrollment")

        return enrollment.course if enrollment else None


class ResultNotificationView(RetrieveModelMixin, PearsonRTENBaseView):
    """
    View for handling Result Notification events.

    This view handles the creation of Result Notification events in the Pearson RTEN system.
    The `event_type` attribute is set to "resultNotification".
    """
    event_type = RESULT_NOTIFICATION
    lookup_field = "course"

    def create(self, request, *args, **kwargs):
        """
        Execute the parent create method and allow to run the result notification pipeline.

        Args:
            request (Request): The request object containing the data.

        Returns:
            Response: Response object with status code 201 and an empty dictionary.
        """
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK and getattr(settings, "ENABLE_CERTIFICATE_PUBLISHER", False):
            result_notification = ResultNotificationBackend(request_data=request.data)
            result_notification.run_pipeline()

        return response

    def get_object(self):
        """
        Retrieves the latest object for the given candidate and course.

        This method filters the queryset to find objects matching the current user
        and the course specified by the lookup field in the URL. If no objects are found,
        it raises a 404 error. If objects are found, it returns the most recently created object.

        Returns:
            object: The most recently created object that matches the given candidate and course.

        Raises:
            Http404: If no objects match the given candidate and course.
        """
        objects = self.get_queryset().filter(
            candidate=self.request.user,
            course=self.kwargs[self.lookup_field],
        )

        if not objects:
            raise Http404

        return objects.latest("created_at")


class PlaceHoldView(PearsonRTENBaseView):
    """
    View for handling Place Hold events.

    This view handles the creation of Place Hold events in the Pearson RTEN system.
    The `event_type` attribute is set to "placeHold".
    """

    event_type = PLACE_HOLD


class ReleaseHoldView(PearsonRTENBaseView):
    """
    View for handling Release Hold events.

    This view handles the creation of Release Hold events in the Pearson RTEN system.
    The `event_type` attribute is set to "releaseHold".
    """

    event_type = RELEASE_HOLD


class ModifyResultStatusView(PearsonRTENBaseView):
    """
    View for handling Modify Result Status events.

    This view handles the creation of Modify Result Status events in the Pearson RTEN system.
    The `event_type` attribute is set to "modifyResultStatus".
    """

    event_type = MODIFY_RESULT_STATUS


class RevokeResultView(PearsonRTENBaseView):
    """
    View for handling Revoke Result events.

    This view handles the creation of Revoke Result events in the Pearson RTEN system.
    The `event_type` attribute is set to "revokeResult".
    """

    event_type = REVOKE_RESULT


class UnrevokeResultView(PearsonRTENBaseView):
    """
    View for handling Unrevoke Result events.

    This view handles the creation of Unrevoke Result events in the Pearson RTEN system.
    The `event_type` attribute is set to "unrevokeResult".
    """

    event_type = UNREVOKE_RESULT


class ModifyAppointmentView(PearsonRTENBaseView):
    """
    View for handling Modify Appointment events.

    This view handles the creation of Modify Appointment events in the Pearson RTEN system.
    The `event_type` attribute is set to "modifyAppointment".
    """

    event_type = MODIFY_APPOINTMENT


class CancelAppointmentView(PearsonRTENBaseView):
    """
    View for handling Cancel Appointment events.

    This view handles the creation of Cancel Appointment events in the Pearson RTEN system.
    The `event_type` attribute is set to "CancelAppointment".
    """

    event_type = CANCEL_APPOINTMENT
