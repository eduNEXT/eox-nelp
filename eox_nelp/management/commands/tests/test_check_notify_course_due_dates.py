"""This file contains the test case for the Nelp command
`notify_course_due_dates`.

TestCases:
- CheckNotifyCourseDueDateTestCase
"""
from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from mock import patch

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.notifications.models import UpcomingCourseDueDate


class CheckNotifyCourseDueDateTestCase(TestCase):
    """ Test `check notify_course_due_dates` command. """
    # pylint: disable=no-member

    def setUp(self):
        """
        Set base variables and objects across UpcomingCourseDueDate test cases.
        """
        self.course = CourseOverview.objects.create(id="course-v1:sky+walker+2023-v")

    @patch.object(UpcomingCourseDueDate, 'notify')
    def test_dates_in_range_to_notify(self, notify_mock):
        """ Test that 2 UpcomingCourseDueDate configured with correct conditions
        are being notified by  calling the command.
        Expected behavior:
            - notify method of UpcomingCourseDueDate is called twice.
        """
        now = timezone.now()
        UpcomingCourseDueDate.objects.all().delete()
        UpcomingCourseDueDate.objects.get_or_create(
            course=self.course,
            location_id="block-v1:star+cd323+2023-1+type@sequential+block@jedis",
            notification_date=now - timedelta(days=1),
            due_date=now + timedelta(days=3),
            sent=False
        )
        UpcomingCourseDueDate.objects.get_or_create(
            course=self.course,
            location_id="block-v1:star+cd323+2023-1+type@sequential+block@jedis2",
            notification_date=now - timedelta(days=3),
            due_date=now + timedelta(days=10),
            sent=False
        )

        call_command('notify_course_due_dates')

        self.assertEqual(notify_mock.call_count, 2)

    @patch.object(UpcomingCourseDueDate, 'notify')
    def test_notification_date_not_in_range(self, notify_mock):
        """ Test UpcomingCourseDueDate is not notified because the notifiction_date has not been reached.
        Expected behavior:
            - notify method of UpcomingCourseDueDate is not called.
        """
        now = timezone.now()
        UpcomingCourseDueDate.objects.all().delete()
        UpcomingCourseDueDate.objects.get_or_create(
            course=self.course,
            location_id="block-v1:star+cd323+2023-1+type@sequential+block@jedis",
            notification_date=now + timedelta(days=1),
            due_date=now + timedelta(days=7),
            sent=False
        )

        call_command('notify_course_due_dates')

        notify_mock.assert_not_called()

    @patch.object(UpcomingCourseDueDate, 'notify')
    def test_due_date_already_past(self, notify_mock):
        """ Test UpcomingCourseDueDate is not notified because the due_date has alredy past,
        even though notification_date is in range.
        Expected behavior:
            - notify method of UpcomingCourseDueDate is not called.
        """
        now = timezone.now()
        UpcomingCourseDueDate.objects.all().delete()
        UpcomingCourseDueDate.objects.get_or_create(
            course=self.course,
            location_id="block-v1:star+cd323+2023-1+type@sequential+block@jedis",
            notification_date=now - timedelta(days=7),
            due_date=now - timedelta(days=1),
            sent=False
        )

        call_command('notify_course_due_dates')

        notify_mock.assert_not_called()

    @patch.object(UpcomingCourseDueDate, 'notify')
    def test_notification_already_sent(self, notify_mock):
        """ Test UpcomingCourseDueDate is not notified because it was alredy sent.
        even though dates are correctly configured in the range.
        Expected behavior:
            - notify method of UpcomingCourseDueDate is not called.
        """
        now = timezone.now()
        UpcomingCourseDueDate.objects.all().delete()
        UpcomingCourseDueDate.objects.get_or_create(
            course=self.course,
            location_id="block-v1:star+cd323+2023-1+type@sequential+block@jedis",
            notification_date=now - timedelta(days=1),
            due_date=now + timedelta(days=3),
            sent=True
        )

        call_command('notify_course_due_dates')

        notify_mock.assert_not_called()
