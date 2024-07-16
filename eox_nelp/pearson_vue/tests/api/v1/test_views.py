"""
This module defines a mixin and test cases for handling Pearson VUE api v1 views.

Classes:
    RTENMixin: A mixin class providing setup and test methods for RTEN event creation.
    TestResultNotificationView: Unit tests for the ResultNotificationView.
    TestPlaceHoldView: Unit tests for the PlaceHoldView.
    TestReleaseHoldView: Unit tests for the ReleaseHoldView.
    TestModifyResultStatusView: Unit tests for the ModifyResultStatusView.
    TestRevokeResultView: Unit tests for the RevokeResultView.
    TestUnrevokeResultView: Unit tests for the UnrevokeResultView.
"""
import unittest
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from django.urls import reverse
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.test import APIClient

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.edxapp_wrapper.student import AnonymousUserId
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

User = get_user_model()


class RTENMixin:
    """
    A mixin class providing setup and test methods for RTEN event creation.
    """
    event_type = None

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set up test client.
        """
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.course_key = CourseKey.from_string("course-v1:test+CS501+2022_T4")
        self.course, _ = CourseOverview.objects.get_or_create(id=self.course_key)

    def tearDown(self):  # pylint: disable=invalid-name
        """
        Reset the mocked objects after each test.
        """
        AnonymousUserId.reset_mock()
        AnonymousUserId.objects.get.side_effect = None

    @patch("eox_nelp.pearson_vue.api.v1.views.get_enrollment_from_id")
    @override_settings(ENABLE_CERTIFICATE_PUBLISHER=False)
    def test_create_result_notification_event(self, enrollment_from_id_mock):
        """
        Test creating an event.

        Expected behavior:
            - The number of records has increased in 1.
            - Response returns a 200 status code.
            - Response data is empty.
            - AnonymousUserId.objects.get has been called with the expected data.
            - get_enrollment_from_id has been called with the expected data.
        """
        # pylint: disable=no-member
        initial_count = PearsonRTENEvent.objects.filter(
            event_type=self.event_type,
            candidate=self.user,
            course=self.course,
        ).count()
        enrollment_from_id_mock.return_value = {"enrollment": Mock(course=self.course)}
        AnonymousUserId.objects.get.return_value.user = self.user

        response = self.client.post(
            reverse(f"pearson-vue-api:v1:{self.event_type}-list"),
            {
                "clientCandidateID": "NELC123456",
                "authorization": {
                    "clientAuthorizationID": "1584-4785"
                },
            },
            format="json",
        )

        final_count = PearsonRTENEvent.objects.filter(
            event_type=self.event_type,
            candidate=self.user,
            course=self.course,
        ).count()

        self.assertEqual(final_count, initial_count + 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
        AnonymousUserId.objects.get.assert_called_once_with(anonymous_user_id="123456")
        enrollment_from_id_mock.assert_called_once_with("1584")

    @override_settings(ENABLE_CERTIFICATE_PUBLISHER=False)
    def test_create_result_notification_event_without_user(self):
        """
        Test creating an event without clienCandidateID.

        Expected behavior:
            - The number of records has increased in 1.
            - Response returns a 200 status code.
            - Response data is empty.
            - AnonymousUserId.objects.get has been called with the expected data.
        """
        # pylint: disable=no-member
        initial_count = PearsonRTENEvent.objects.filter(event_type=self.event_type, candidate=None).count()
        AnonymousUserId.DoesNotExist = ObjectDoesNotExist
        AnonymousUserId.objects.get.side_effect = AnonymousUserId.DoesNotExist

        response = self.client.post(reverse(f"pearson-vue-api:v1:{self.event_type}-list"), {}, format="json")

        final_count = PearsonRTENEvent.objects.filter(event_type=self.event_type, candidate=None).count()

        self.assertEqual(final_count, initial_count + 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
        AnonymousUserId.objects.get.assert_called_once_with(anonymous_user_id="")

    @patch("eox_nelp.pearson_vue.api.v1.views.get_enrollment_from_id")
    @override_settings(ENABLE_CERTIFICATE_PUBLISHER=False)
    def test_create_result_notification_event_with_invalid_authorization_id(self, enrollment_from_id_mock):
        """
        Test creating an event with invalid clienAuthorizationID.

        Expected behavior:
            - The number of records has increased in 1.
            - Response returns a 200 status code.
            - Response data is empty.
            - the course record is None
            - get_enrollment_from_id has been called with the expected data.
        """
        # pylint: disable=no-member
        initial_record_ids = list(
            PearsonRTENEvent.objects.filter(event_type=self.event_type).values_list('id', flat=True)
        )
        enrollment_from_id_mock.return_value = {}

        response = self.client.post(
            reverse(f"pearson-vue-api:v1:{self.event_type}-list"),
            {"authorization": {"clientAuthorizationID": "1584-4785"}},
            format="json",
        )

        new_records = PearsonRTENEvent.objects.filter(event_type=self.event_type).exclude(id__in=initial_record_ids)

        self.assertEqual(1, new_records.count())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
        self.assertIsNone(new_records[0].course)
        enrollment_from_id_mock.assert_called_once_with("1584")

    def test_get_event(self):
        """
        Test retrieving an event.

        Expected behavior:
            - The response returns a 200 status code.
            - The response data contains the correct event details.
        """
        # This will create a record to ensure that  there is at least one element
        PearsonRTENEvent.objects.create(event_type=self.event_type, content={})  # pylint: disable=no-member
        # Retrieve all the events of the same type
        events = PearsonRTENEvent.objects.filter(event_type=self.event_type)  # pylint: disable=no-member
        expected_results = []

        for event in events:
            expected_results.append({
                'event_type': event.event_type,
                'content': event.content,
                'created_at': event.created_at.isoformat(),
            })

        response = self.client.get(reverse(f"pearson-vue-api:v1:{self.event_type}-list"), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(events))

    @override_settings(PEARSON_RTEN_API_ENABLED=False)
    def test_create_result_notification_event_disabled(self):
        """
        Test creating an event when PEARSON_RTEN_ENABLED is False.

        Expected behavior:
            - No new record is created.
            - Response returns a 404 status code.
        """
        initial_count = PearsonRTENEvent.objects.filter(event_type=self.event_type).count()  # pylint: disable=no-member

        response = self.client.post(reverse(f"pearson-vue-api:v1:{self.event_type}-list"), {}, format="json")

        final_count = PearsonRTENEvent.objects.filter(event_type=self.event_type).count()  # pylint: disable=no-member

        self.assertEqual(final_count, initial_count)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(PEARSON_RTEN_API_ENABLED=False)
    def test_get_event_disabled(self):
        """
        Test retrieving an event when PEARSON_RTEN_ENABLED is False.

        Expected behavior:
            - Response returns a 404 status code.
        """
        response = self.client.get(reverse(f"pearson-vue-api:v1:{self.event_type}-list"), format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestResultNotificationView(RTENMixin, unittest.TestCase):
    """
    Unit tests for ResultNotificationView.
    """
    event_type = RESULT_NOTIFICATION

    @patch("eox_nelp.pearson_vue.api.v1.views.ResultNotificationBackend")
    def test_pipeline_execution(self, result_notification_mock):
        """
        Test that a new event is created and the result notification pipeline is run
        when ENABLE_CERTIFICATE_PUBLISHER is True.

        Expected behavior:
            - The number of records has increased in 1.
            - Response returns a 200 status code.
            - Response data is empty.
            - ResultNotificationBackend was initialized with the right data
            - run_pipeline method was called once.

        """
        # pylint: disable=no-member
        initial_count = PearsonRTENEvent.objects.filter(event_type=self.event_type).count()
        payload = {
            "eventType": "RESULT_AVAILABLE",
            "candidate": {
                "candidateName": {
                    "firstName": "Alastor",
                    "lastName": "Moody",
                }
            }
        }

        response = self.client.post(reverse(f"pearson-vue-api:v1:{self.event_type}-list"), payload, format="json")

        final_count = PearsonRTENEvent.objects.filter(event_type=self.event_type).count()

        self.assertEqual(final_count, initial_count + 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
        result_notification_mock.assert_called_once_with(request_data=payload)
        result_notification_mock.return_value.run_pipeline.assert_called_once()


class TestPlaceHoldView(RTENMixin, unittest.TestCase):
    """
    Unit tests for PlaceHoldView.
    """
    event_type = PLACE_HOLD


class TestReleaseHoldView(RTENMixin, unittest.TestCase):
    """
    Unit tests for ReleaseHoldView.
    """
    event_type = RELEASE_HOLD


class TestModifyResultStatusView(RTENMixin, unittest.TestCase):
    """
    Unit tests for ModifyResultStatusView.
    """
    event_type = MODIFY_RESULT_STATUS


class TestRevokeResultView(RTENMixin, unittest.TestCase):
    """
    Unit tests for RevokeResultView.
    """
    event_type = REVOKE_RESULT


class TestUnrevokeResultView(RTENMixin, unittest.TestCase):
    """
    Unit tests for UnrevokeResultView.
    """
    event_type = UNREVOKE_RESULT


class TestModifyAppointmentView(RTENMixin, unittest.TestCase):
    """
    Unit tests for ModifyAppointmentView.
    """
    event_type = MODIFY_APPOINTMENT


class TestCancelAppointmentView(RTENMixin, unittest.TestCase):
    """
    Unit tests for CancelAppointmentView.
    """
    event_type = CANCEL_APPOINTMENT
