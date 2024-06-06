"""
Unit tests for the student admin module.

Classes:
    TestPearsonAction: Tests for pearson_action admin actions.
    TestNelpCourseEnrollmentAdmin: Tests for the NelpCourseEnrollmentAdmin admin class.
"""
from unittest.mock import MagicMock, patch

from ddt import data, ddt, unpack
from django.test import RequestFactory, TestCase

from eox_nelp.admin import (
    NelpCourseEnrollmentAdmin,
    pearson_add_ead_action,
    pearson_cdd_action,
    pearson_delete_ead_action,
    pearson_real_time_action,
    pearson_update_ead_action,
)


@ddt
class TestPearsonAction(TestCase):
    """
    Unit tests for the pearson actions functions.
    """

    @data(
        {
            "mock_task": "eox_nelp.pearson_vue.tasks.real_time_import_task.delay",
            "admin_action": pearson_real_time_action,
            "call_args": ["user_id", "course_id"],
            "extra_call_kwargs": {
            },
        },
        {
            "mock_task": "eox_nelp.pearson_vue.tasks.ead_task.delay",
            "admin_action": pearson_add_ead_action,
            "call_args": ["user_id", "course_id"],
            "extra_call_kwargs": {
                "transaction_type": "Add",
            },

        },
        {
            "mock_task": "eox_nelp.pearson_vue.tasks.ead_task.delay",
            "admin_action": pearson_update_ead_action,
            "call_args": ["user_id", "course_id"],
            "extra_call_kwargs": {
                "transaction_type": "Update",
            },
        },
        {
            "mock_task": "eox_nelp.pearson_vue.tasks.ead_task.delay",
            "admin_action": pearson_delete_ead_action,
            "call_args": ["user_id", "course_id"],
            "extra_call_kwargs": {
                "transaction_type": "Delete",
            },
        },
        {
            "mock_task": "eox_nelp.pearson_vue.tasks.cdd_task.delay",
            "admin_action": pearson_cdd_action,
            "call_args": ["user_id"],
            "extra_call_kwargs": {
            },
        },
    )
    @unpack
    def test_pearson_course_enrollment_action(self, mock_task, admin_action, call_args, extra_call_kwargs):
        """
        Test that a pearson_action function calls the a task delay with correct parameters.
        """
        user = MagicMock()
        user.id = 1
        course_enrollment_1 = MagicMock()
        course_enrollment_1.course_id = "course-v1:TestX+T101+2024_T1"
        course_enrollment_1.user = user
        course_enrollment_2 = MagicMock()
        course_enrollment_2.course_id = "course-v1:FutureX+T102+2025_T1"
        course_enrollment_2.user = user
        mocks_call_kwargs = [
            {
                "course_id": course_enrollment_1.course_id,
                "user_id": user.id,
            },
            {
                "course_id": course_enrollment_2.course_id,
                "user_id": user.id,
            }
        ]
        for mock_call_kwargs in mocks_call_kwargs:
            for key in set(mock_call_kwargs.keys()).difference(call_args):  # set main call args
                del mock_call_kwargs[key]
            mock_call_kwargs.update(extra_call_kwargs)

        queryset = [course_enrollment_1, course_enrollment_2]
        modeladmin = MagicMock()

        request = RequestFactory().get("/admin")

        # Call the admin action
        with patch(mock_task) as mocked_task:
            admin_action(modeladmin, request, queryset)
            for mock_call_kwargs in mocks_call_kwargs:
                mocked_task.assert_any_call(**mock_call_kwargs)
                mocked_task.assert_any_call(**mock_call_kwargs)
            self.assertEqual(mocked_task.call_count, len(mocks_call_kwargs))


@ddt
class TestNelpCourseEnrollmentAdmin(TestCase):
    """
    Unit tests for the NelpCourseEnrollmentAdmin class.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        self.modeladmin = NelpCourseEnrollmentAdmin()

    @data(
        pearson_add_ead_action,
        pearson_cdd_action,
        pearson_delete_ead_action,
        pearson_real_time_action,
        pearson_update_ead_action,
    )
    def test_actions(self, admin_action):
        """
        Test that the actions list contains pearson_real_time_action.

        Expected behavior:
            - pearson_real_time_action method is in model actions.
        """
        self.assertIn(admin_action, self.modeladmin.actions)
