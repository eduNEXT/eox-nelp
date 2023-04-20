"""This file contains all the test for notifications/models.py file.

Classes:
    UpcomingCourseDueDateTestCase: Test UpcomingCourseDueDate django model.
"""
import datetime
import unittest

from ddt import data, ddt
from django.utils import timezone
from mock import Mock
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.notifications.models import UpcomingCourseDueDate
from eox_nelp.notifications.tasks import create_course_notifications


@ddt
class CreateCourseNotificationsTestCase(unittest.TestCase):
    """Test class for function create_course_notifications."""

    def setUp(self):
        """ Set common conditions for test cases."""
        self.course = Mock()
        self.course_id = "course-v1:test+Cx105+2022_T4"
        modulestore.return_value.get_course.return_value = self.course

    def tearDown(self):
        """Restore mocks' state"""
        modulestore.reset_mock()
        self.course.reset_mock()

    def test_invalid_course_id(self):
        """Test when the course_id parameter is invalid

        Expected behavior:
            - Raise InvalidKeyError .
        """
        course_id = "This is not Valid"

        self.assertRaises(InvalidKeyError, create_course_notifications, course_id)

    def test_empty_notifications_settings(self):
        """Test a course that has not been set with notifications

        Expected behavior:
            - Get items (subsections) has not been called.
            - There are no new UpcomingCourseDueDate records.
        """
        self.course.other_course_settings = {}
        current_records = list(
            UpcomingCourseDueDate.objects.all().values_list("id", flat=True)  # pylint: disable=no-member
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_not_called()
        self.assertEqual(
            current_records,
            list(UpcomingCourseDueDate.objects.all().values_list("id", flat=True)),  # pylint: disable=no-member
        )

    @data(False, None, "", 0)
    def test_invalid_active_field(self, active_value):
        """Test a course with invalid active notifications value.

        Expected behavior:
            - Get items (subsections) has not been called.
            - There are no new UpcomingCourseDueDate records.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": active_value
            }
        }
        current_records = list(
            UpcomingCourseDueDate.objects.all().values_list("id", flat=True)  # pylint: disable=no-member
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_not_called()
        self.assertEqual(
            current_records,
            list(UpcomingCourseDueDate.objects.all().values_list("id", flat=True)),  # pylint: disable=no-member
        )

    @data(True, "valid", 1)
    def test_empty_subsections(self, active_value):
        """Test a course without subsections.

        Expected behavior:
            - Get items (subsections) was called with the right parameters.
            - There are no new UpcomingCourseDueDate records.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": active_value
            }
        }
        course_key = CourseKey.from_string(self.course_id)
        modulestore.return_value.get_items.return_value = self._generate_subsections([])
        current_records = list(
            UpcomingCourseDueDate.objects.all().values_list("id", flat=True)  # pylint: disable=no-member
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_called_once_with(
            course_key,
            qualifiers={"category": "sequential"},
        )
        self.assertEqual(
            current_records,
            list(UpcomingCourseDueDate.objects.all().values_list("id", flat=True)),  # pylint: disable=no-member
        )

    @data(True, "valid", 1)
    def test_subsections_without_due_date(self, active_value):
        """Test a course with subsections but the subsections doesn't have due date.

        Expected behavior:
            - Get items (subsections) was called with the right parameters.
            - There are no new UpcomingCourseDueDate records.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": active_value
            }
        }
        course_key = CourseKey.from_string(self.course_id)
        modulestore.return_value.get_items.return_value = self._generate_subsections(
            [{"due": None}, {"due": None}]
        )
        current_records = list(
            UpcomingCourseDueDate.objects.all().values_list("id", flat=True)  # pylint: disable=no-member
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_called_once_with(
            course_key,
            qualifiers={"category": "sequential"},
        )
        self.assertEqual(
            current_records,
            list(UpcomingCourseDueDate.objects.all().values_list("id", flat=True)),  # pylint: disable=no-member
        )

    @data(True, "valid", 1)
    def test_create_multiple_notifications(self, active_value):
        """Test a course with two subsections with due date

        Expected behavior:
            - Get items (subsections) was called with the right parameters.
            - Two new UpcomingCourseDueDate records were created.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": active_value
            }
        }
        due_date = timezone.now() + datetime.timedelta(days=18)
        expected_notification_date = due_date - datetime.timedelta(days=7)
        course_key = CourseKey.from_string(self.course_id)
        location_1 = "block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a"
        location_2 = "block-v1:test+CS501+2022_T4+type@sequential+block@ww47308785454564646343dd581b4rrr"
        modulestore.return_value.get_items.return_value = self._generate_subsections(
            [
                {
                    "due": due_date,
                    "location": location_1
                },
                {
                    "due": due_date,
                    "location": location_2
                },
            ]
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_called_once_with(
            course_key,
            qualifiers={"category": "sequential"},
        )
        for location in [location_1, location_2]:
            self.assertTrue(
                UpcomingCourseDueDate.objects.get(  # pylint: disable=no-member
                    course_id=self.course_id,
                    location_id=location,
                    due_date=due_date,
                    notification_date=expected_notification_date,
                )
            )

    @data(True, "valid", 1)
    def test_past_notification_date(self, active_value):
        """Test a course with a subsection which have a nearly due_date
        therefore the notification date is in the past

        Expected behavior:
            - Get items (subsections) was called with the right parameters.
            - There are no new UpcomingCourseDueDate records.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": active_value
            }
        }
        due_date = timezone.now()
        expected_notification_date = due_date - datetime.timedelta(days=7)
        course_key = CourseKey.from_string(self.course_id)
        location = "block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a"
        modulestore.return_value.get_items.return_value = self._generate_subsections(
            [
                {
                    "due": due_date,
                    "location": location
                },
            ]
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_called_once_with(
            course_key,
            qualifiers={"category": "sequential"},
        )
        self.assertFalse(
            UpcomingCourseDueDate.objects.filter(  # pylint: disable=no-member
                course_id=self.course_id,
                location_id=location,
                due_date=due_date,
                notification_date=expected_notification_date,
            )
        )

    @data(True, "valid", 1)
    def test_update_notification(self, active_value):
        """Test when there is already a UpcomingCourseDueDate record, but the due date changed.

        Expected behavior:
            - Get items (subsections) was called with the right parameters.
            - A new UpcomingCourseDueDate record is created.
            - Previous UpcomingCourseDueDate record is deleted.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": active_value
            }
        }
        location = "block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a"
        due_date = timezone.now()
        # Create old record
        UpcomingCourseDueDate.objects.create(  # pylint: disable=no-member
            course_id=self.course_id,
            location_id=location,
            due_date=due_date,
            notification_date=due_date,
        )
        new_due_date = timezone.now() + datetime.timedelta(days=18)
        expected_notification_date = new_due_date - datetime.timedelta(days=7)
        course_key = CourseKey.from_string(self.course_id)
        modulestore.return_value.get_items.return_value = self._generate_subsections(
            [
                {
                    "due": new_due_date,
                    "location": location
                },
            ]
        )

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_called_once_with(
            course_key,
            qualifiers={"category": "sequential"},
        )
        self.assertTrue(
            UpcomingCourseDueDate.objects.filter(  # pylint: disable=no-member
                course_id=self.course_id,
                location_id=location,
                due_date=new_due_date,
                notification_date=expected_notification_date,
            )
        )
        self.assertFalse(
            UpcomingCourseDueDate.objects.filter(  # pylint: disable=no-member
                course_id=self.course_id,
                location_id=location,
                due_date=due_date,
                notification_date=due_date,
            )
        )

    @data("5", 5, [5], [5, 8], [5, "3"])
    def test_days_in_advance(self, days_in_advance):
        """Test multiple configuration for days_in_advance.

        Expected behavior:
            - Get items (subsections) was called with the right parameters.
            - The number of new UpcomingCourseDueDate records correspond to the number of days in advance.
        """
        self.course.other_course_settings = {
            "notifications": {
                "active": True,
                "days_in_advance": days_in_advance
            }
        }
        location = "block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a"
        due_date = timezone.now() + datetime.timedelta(days=18)
        course_key = CourseKey.from_string(self.course_id)
        modulestore.return_value.get_items.return_value = self._generate_subsections(
            [
                {
                    "due": due_date,
                    "location": location
                },
            ]
        )

        if not isinstance(days_in_advance, list):
            days_in_advance = [days_in_advance]

        create_course_notifications(course_id=self.course_id)

        modulestore.return_value.get_items.assert_called_once_with(
            course_key,
            qualifiers={"category": "sequential"},
        )

        for day_in_advance in days_in_advance:
            self.assertTrue(
                UpcomingCourseDueDate.objects.filter(  # pylint: disable=no-member
                    course_id=self.course_id,
                    location_id=location,
                    due_date=due_date,
                    notification_date=due_date - datetime.timedelta(days=int(day_in_advance)),
                )
            )

    def _generate_subsections(self, subsections_data):
        """Helper method to create Mock subsection based on the given data.

        Args:
            subsections_data: This should be a list of dicts with the following structure:

            [
                {
                    "due": due_date,
                    "location": location
                },
                {
                    "due": due_date,
                    "location": location
                },
                ...
            ]
            Every dictionary should contain the subsection data.

        Returns:
            List of mocks.
        """
        subsections = []

        for subsection_data in subsections_data:
            subsection = Mock()
            subsection.due = subsection_data.get("due")
            subsection.location = subsection_data.get("location")

            subsections.append(subsection)

        return subsections
