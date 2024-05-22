"""
Unit tests for the student admin module.

Classes:
    TestPearsonRealTimeAction: Tests for the pearson_real_time_action admin action.
    TestNelpCourseEnrollmentAdmin: Tests for the NelpCourseEnrollmentAdmin admin class.
"""
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from eox_nelp.admin import NelpCourseEnrollmentAdmin, pearson_real_time_action


class TestPearsonRealTimeAction(TestCase):
    """
    Unit tests for the pearson_real_time_action function.
    """

    @patch("eox_nelp.pearson_vue.tasks.real_time_import_task.delay")
    def test_pearson_real_time_action(self, mock_delay):
        """
        Test that the pearson_real_time_action function calls the real_time_import_task.delay with correct parameters.
        """
        user = MagicMock()
        user.id = 1
        course_enrollment_1 = MagicMock()
        course_enrollment_1.course_id = "course-v1:TestX+T101+2024_T1"
        course_enrollment_1.user = user
        course_enrollment_2 = MagicMock()
        course_enrollment_2.course_id = "course-v1:FutureX+T102+2025_T1"
        course_enrollment_2.user = user

        queryset = [course_enrollment_1, course_enrollment_2]
        modeladmin = MagicMock()

        request = RequestFactory().get("/admin")

        # Call the admin action
        pearson_real_time_action(modeladmin, request, queryset)

        mock_delay.assert_any_call(course_id=course_enrollment_1.course_id, user_id=user.id)
        mock_delay.assert_any_call(course_id=course_enrollment_2.course_id, user_id=user.id)
        self.assertEqual(mock_delay.call_count, 2)


class TestNelpCourseEnrollmentAdmin(TestCase):
    """
    Unit tests for the NelpCourseEnrollmentAdmin class.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        self.modeladmin = NelpCourseEnrollmentAdmin()

    def test_actions(self):
        """
        Test that the actions list contains pearson_real_time_action.

        Expected behavior:
            - pearson_real_time_action method is in model actions.
        """
        self.assertIn(pearson_real_time_action, self.modeladmin.actions)
