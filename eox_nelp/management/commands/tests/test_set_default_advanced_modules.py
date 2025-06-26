"""This file contains test cases for the Nelp command `set_default_advanced_modules`.

TestCases:
- SetDefaultAdvancedModulesCommandTestCase
"""

from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.edxapp_wrapper.modulestore import ModuleStoreEnum


class SetDefaultAdvancedModulesCommandTestCase(TestCase):
    """Test `set_default_advanced_modules` management command."""

    def setUp(self):
        """Create a dummy course for tests."""
        self.course = CourseOverview.objects.create(id="course-v1:test+demo+2025")
        CourseOverview.objects.create(id="course-v1:test+advanced_demo+2025")
        ModuleStoreEnum.UserID.mgmt_command = 5

    @patch("eox_nelp.signals.tasks.set_default_advanced_modules.delay")
    def test_run_with_valid_course_id(self, mock_task):
        """
        Test command runs with --course-id.

        Expected behavior:
        - The task is called once with the right data.
        """
        call_command("set_default_advanced_modules", "--course-id", str(self.course.id))

        mock_task.assert_called_once_with(
            course_id=str(self.course.id),
            user_id=ModuleStoreEnum.UserID.mgmt_command,
        )

    @patch("eox_nelp.signals.tasks.set_default_advanced_modules.delay")
    def test_run_with_all_flag(self, mock_task):
        """
        Test command runs with --all flag.

        Expected behavior:
        - The task is called once for each course.
        - The task receives correct course_id.
        - The task receives constant user_id.
        """
        courses = list(CourseOverview.objects.all())
        expected_calls = [
            {
                "course_id": str(course.id),
                "user_id": ModuleStoreEnum.UserID.mgmt_command,
            } for course in courses
        ]

        call_command("set_default_advanced_modules", "--all")

        actual_calls = [call.kwargs for call in mock_task.call_args_list]
        self.assertEqual(mock_task.call_count, len(courses))
        self.assertCountEqual(actual_calls, expected_calls)

    def test_requires_course_id_without_all(self):
        """
        Test command fails when neither --course-id nor --all is given.

        Expected behavior:
        - CommandError is raised with proper message.
        """
        with self.assertRaisesMessage(CommandError, "You must provide --course-id unless using --all"):
            call_command("set_default_advanced_modules")

    def test_fails_with_invalid_course_id(self):
        """
        Test command fails if course_id does not exist.

        Expected behavior:
        - CommandError is raised.
        - The error message includes the invalid ID.
        """
        with self.assertRaisesMessage(
            CommandError,
            "CourseOverview with id 'course-v1:invalid+id+2025' not found."
        ):
            call_command("set_default_advanced_modules", "--course-id", "course-v1:invalid+id+2025")
