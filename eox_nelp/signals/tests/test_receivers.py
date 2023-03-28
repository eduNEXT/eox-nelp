"""This file contains all the test for receivers.py file.
Classes:
    CourseGradeChangedProgressPublisherTestCase: Test course_grade_changed_progress_publisher receiver.
    BlockcompletionProgressPublisherTestCase: Test block_completion_progress_publisher receiver.
"""
import unittest

from django.contrib.auth import get_user_model
from mock import patch
from opaque_keys.edx.keys import CourseKey

from eox_nelp.edxapp_wrapper.test_backends import create_test_model
from eox_nelp.signals.receivers import block_completion_progress_publisher, course_grade_changed_progress_publisher

User = get_user_model()


class CourseGradeChangedProgressPublisherTestCase(unittest.TestCase):
    """Test class for course_grade_changed_progress_publisher"""

    @patch("eox_nelp.signals.receivers.dispatch_futurex_progress")
    def test_call_dispatch(self, dispatch_mock):
        """Test when course_grade_changed_progress_publisher is called
        with the required parameters.

        Expected behavior:
            - dispatch_futurex_progress is called with the right values.
        """
        user, _ = User.objects.get_or_create(username="Salazar")
        course_key = CourseKey.from_string("course-v1:test+Cx105+2022_T4")
        course_grade = create_test_model('CourseGrade', 'eox_nelp', __package__, fields={"passed": True})

        course_grade_changed_progress_publisher(user, course_key, course_grade)

        dispatch_mock.assert_called_with(
            course_id=str(course_key),
            user_id=user.id,
            is_complete=True,
        )


class BlockcompletionProgressPublisherTestCase(unittest.TestCase):
    """Test class for block_completion_progress_publisher"""

    @patch("eox_nelp.signals.receivers.dispatch_futurex_progress")
    def test_call_dispatch(self, dispatch_mock):
        """Test when block_completion_progress_publisher is called
        with the required parameters.

        Expected behavior:
            - dispatch_futurex_progress is called with the right values.
        """
        course_key = CourseKey.from_string("course-v1:test+Cx105+2022_T4")
        block_completion = create_test_model(
            "BlockCompletion",
            "eox_nelp",
            __package__,
            fields={"user_id": 13, "context_key": course_key},
        )

        block_completion_progress_publisher(block_completion)

        dispatch_mock.delay.assert_called_with(
            course_id=str(course_key),
            user_id=13,
        )
