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

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from eox_nelp.pearson_vue.constants import (
    MODIFY_RESULT_STATUS,
    PLACE_HOLD,
    RELEASE_HOLD,
    RESULT_NOTIFICATION,
    REVOKE_RESULT,
    UNREVOKE_RESULT,
)
from eox_nelp.pearson_vue.models import PearsonRTENModel

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

    def test_create_result_notification_event(self):
        """
        Test creating an event.

        Expected behavior:
            - The number of recors has incrsed in 1.
            - Response returns a 200 status code.
            - Response data is empty.

        """
        # pylint: disable=no-member
        initial_count = PearsonRTENModel.objects.filter(event_type=self.event_type).count()

        response = self.client.post(reverse(f"pearson-vue-api:v1:{self.event_type}"), {}, format="json")

        final_count = PearsonRTENModel.objects.filter(event_type=self.event_type).count()

        self.assertEqual(final_count, initial_count + 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})


class TestResultNotificationView(RTENMixin, unittest.TestCase):
    """
    Unit tests for ResultNotificationView.
    """
    event_type = RESULT_NOTIFICATION


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
