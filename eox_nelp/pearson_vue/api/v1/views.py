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
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


class PearsonRTENBaseView(generics.ListCreateAPIView):
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

    def dispatch(self, request, *args, **kwargs):
        """
        Override the dispatch method to check if the PEARSON_RTEN_API_ENABLED setting is active.

        This method checks if the PEARSON_RTEN_API_ENABLED setting is set to True. If it is not,
        it raises an Http404 exception, resulting in a 404 Not Found response. If the setting
        is active, it proceeds with the normal dispatch process.

        Args:
            request (Request): The request object containing the data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: Parent dispatch result.

        Raises:
            Http404: If the PEARSON_RTEN_API_ENABLED setting is not active.
        """
        if not getattr(settings, "PEARSON_RTEN_API_ENABLED", False):
            raise Http404

        return super().dispatch(request, *args, **kwargs)

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
        serializer.save(event_type=self.event_type, content=content_data)

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({}, status=status.HTTP_200_OK, headers=headers)


class ResultNotificationView(PearsonRTENBaseView):
    """
    View for handling Result Notification events.

    This view handles the creation of Result Notification events in the Pearson RTEN system.
    The `event_type` attribute is set to "resultNotification".
    """

    event_type = RESULT_NOTIFICATION


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
