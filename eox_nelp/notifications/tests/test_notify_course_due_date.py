"""This file contains all the test for notifications/notify_course_due_date.py file.

Classes:
    NotifyUpcomingCourseDueDateTestCase: Test `notify_upcoming_course_due_date` method.
"""
from datetime import timedelta

from ddt import data, ddt
from django.test import TestCase
from django.utils import timezone
from mock import patch

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.notifications import notify_course_due_date
from eox_nelp.notifications.models import UpcomingCourseDueDate
from eox_nelp.notifications.notify_course_due_date import notify_upcoming_course_due_date
from eox_nelp.tests.utils import generate_list_mock_data

FALSY_SENT_MAILS_VALUES = [0, "", None, [], False, {}, ()]


@ddt
class NotifyUpcomingCourseDueDateTestCase(TestCase):
    """Test class for function `notify_upcoming_course_due_date`."""

    def setUp(self):
        """Set common conditions for test cases."""
        self.patchers = [
            patch("eox_nelp.notifications.notify_course_due_date.send_email_multialternative"),
            patch("eox_nelp.notifications.notify_course_due_date.CourseEmailTemplate"),
            patch("eox_nelp.notifications.notify_course_due_date.get_xblock_course_from_usage_key_string"),
            patch("eox_nelp.notifications.notify_course_due_date.get_xblock_from_usage_key_string"),
            patch("eox_nelp.notifications.notify_course_due_date.CourseEnrollment"),
            patch("eox_nelp.notifications.notify_course_due_date.get_course_email_context"),
        ]
        self.send_email_multialternative_mock = self.patchers[0].start()
        self.course_email_template_mock = self.patchers[1].start()
        self.get_xblock_course_from_usage_key_string_mock = self.patchers[2].start()
        self.get_xblock_from_usage_key_string_mock = self.patchers[3].start()
        self.course_enrollment_mock = self.patchers[4].start()
        self.get_course_email_context_mock = self.patchers[5].start()

    def tearDown(self):
        """Stop patching."""
        for patcher in self.patchers:
            patcher.stop()

    def test_notify_upcoming_course_due_date(self):
        """Test correct behaviour of sending email with
        method `notify_upcoming_course_due_date`.
        Expected behavior:
            - course_email_template.render_plaintext is called with the right values.
            - course_email_template.render_htmltext is called with the right values.
            - send_email_multialternative is called with the right values.
            - The email was sent from the correct email address (if specified)
            - sent attribute of instance of `UpcomingCourseDueDate` after the process is True.
            - Log successful of sent message.
        """
        subsection_due_date = timezone.now() + timedelta(days=4)
        instance, _ = UpcomingCourseDueDate.objects.update_or_create(  # pylint: disable=no-member
            course=CourseOverview.objects.create(id="course-v1:test+Cx105+2022_T4"),
            location_id="block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a",
            due_date=subsection_due_date,
            notification_date=timezone.now(),
            sent=False,
            defaults={"sent": False},
        )
        course_name = "course-display-name"
        subsection_name = "subsection-display-name"
        recipients_list = ["vader@star.com", "palpatine@star.com"]
        delta = subsection_due_date - timezone.now()
        time_remaining = (
            f"{delta.days} days, {delta.seconds // 3600:02d} hours, "
            f"and {(delta.seconds // 60) % 60:02d} mins"
        )
        expected_text_msg = (
            f"The course {course_name} has a notification. "
            f"The subsection {subsection_name} is coming soon. "
            f"The due date of this subsection is UTC {subsection_due_date}. "
            f"There are approx {time_remaining} for the due date of the subsection."
        )
        expected_html_msg = (
            f"<p>The course {course_name} has a notification. "
            f"The subsection {subsection_name} is coming soon.</p>\n"
            f"<p>The due date of this subsection is UTC {subsection_due_date}. "
            f"There are approx {time_remaining} for the due date of the subsection.</p>"
        )
        expected_subject = (
            f"[Futurex platform] Notification due date(left {delta.days} days) of subsection {subsection_name} "
            f"from course {course_name}"
        )
        expected_email_context = {"course_image_url": "https://testing.image.jpg"}
        sent_emails = 1
        self.course_enrollment_mock.objects.filter.return_value = generate_list_mock_data(
            [
                {"user": {"email": recipients_list[0]}},
                {"user": {"email": recipients_list[1]}},
            ],
        )
        self.get_xblock_from_usage_key_string_mock.return_value = generate_list_mock_data(
            [
                {
                    "display_name": subsection_name,
                    "due": subsection_due_date,
                },
            ],
        )[0]
        self.get_xblock_course_from_usage_key_string_mock.return_value = generate_list_mock_data(
            [
                {
                    "display_name": course_name,
                },
            ],
        )[0]
        self.get_course_email_context_mock.return_value = expected_email_context
        self.course_email_template_mock.render_plaintext.return_value = expected_text_msg
        self.course_email_template_mock.render_htmltext.return_value = expected_html_msg
        self.send_email_multialternative_mock.return_value = sent_emails

        with self.assertLogs(notify_course_due_date.__name__, level="INFO") as logs:
            notify_upcoming_course_due_date(instance)

        self.course_email_template_mock.get_template().render_plaintext.assert_called_with(
            expected_text_msg,
            expected_email_context,
        )
        self.course_email_template_mock.get_template().render_htmltext.assert_called_with(
            expected_html_msg,
            expected_email_context,
        )
        self.send_email_multialternative_mock(
            expected_subject,
            expected_text_msg,
            expected_html_msg,
            recipients_list,
        )
        self.assertTrue(instance.sent)
        succesful_log = f"{sent_emails} emails sent related the upcoming_course_due_date: {instance.__dict__} -------"
        self.assertEqual(logs.output, [f"INFO:{notify_course_due_date.__name__}:{succesful_log}"])

    def test_not_notify_upcoming_course_due_date(self):
        """Test not notify of sending email due empty course_enrollments,
        subsection_xblock or course_xblock .
        Expected behavior:
            - course_email_template is not called.
            - send_email_multialternative is not called.
            - sent attribute of instance of `UpcomingCourseDueDate` after the process is False.
            - Log of error of empty retrieving sent message.
        """
        subsection_due_date = timezone.now() + timedelta(days=4)
        instance, _ = UpcomingCourseDueDate.objects.update_or_create(  # pylint: disable=no-member
            course=CourseOverview.objects.create(id="course-v1:test+Cx105+2022_T4"),
            location_id="block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a",
            due_date=subsection_due_date,
            notification_date=timezone.now(),
            sent=False,
            defaults={"sent": False},
        )
        self.course_enrollment_mock.objects.filter.return_value = []
        self.get_xblock_from_usage_key_string_mock.return_value = None
        self.get_xblock_course_from_usage_key_string_mock.return_value = None
        error_log = "is missing one of the following: subsection-xblock(None),recipient_emails([]),course_xblock(None)"

        with self.assertLogs(notify_course_due_date.__name__, level="INFO") as logs:
            notify_upcoming_course_due_date(instance)

        self.course_email_template_mock.assert_not_called()
        self.send_email_multialternative_mock.assert_not_called()
        self.assertFalse(instance.sent)
        self.assertEqual(logs.output, [f"INFO:{notify_course_due_date.__name__}:{error_log}"])

    @data(*FALSY_SENT_MAILS_VALUES)
    def test_not_email_sent_upcoming_course_due_date(self, falsy_sent):
        """Test not notify of sending email due not email sent. Error or sending problem.
        Expected behavior:
            - sent attribute of instance of `UpcomingCourseDueDate` after the process is False.
            - Log of not email sent message.
        """
        subsection_due_date = timezone.now() + timedelta(days=4)
        instance, _ = UpcomingCourseDueDate.objects.update_or_create(  # pylint: disable=no-member
            course=CourseOverview.objects.create(id="course-v1:test+Cx105+2022_T4"),
            location_id="block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a",
            due_date=subsection_due_date,
            notification_date=timezone.now(),
            sent=False,
            defaults={"sent": False},
        )
        course_name = "course-display-name"
        subsection_name = "subsection-display-name"
        recipients_list = ["vader@star.com", "palpatine@star.com"]
        enrollments_data = [
            {"user": {"email": recipients_list[0]}},
            {"user": {"email": recipients_list[1]}},
        ]
        subsection_xblock_data = [
            {
                "display_name": subsection_name,
                "due": subsection_due_date,
            },
        ]
        course_xblock_data = [
            {
                "display_name": course_name,
            },
        ]
        self.course_enrollment_mock.objects.filter.return_value = generate_list_mock_data(enrollments_data)
        self.get_xblock_from_usage_key_string_mock.return_value = generate_list_mock_data(subsection_xblock_data)[0]
        self.get_xblock_course_from_usage_key_string_mock.return_value = generate_list_mock_data(course_xblock_data)[0]
        self.send_email_multialternative_mock.return_value = falsy_sent
        not_sent_log = f"------- No emails were sent!!!, the email function returned {falsy_sent} -------"

        with self.assertLogs(notify_course_due_date.__name__, level="INFO") as logs:
            notify_upcoming_course_due_date(instance)

        self.assertFalse(instance.sent)
        self.assertEqual(logs.output, [f"INFO:{notify_course_due_date.__name__}:{not_sent_log}"])
