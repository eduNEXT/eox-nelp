"""This file contains all the test for tasks.py file.

Classes:
    SendCourseDueDateEmailtTestCase: Test `send_course_due_date_emails` method.

"""
import unittest

from eox_nelp.notifications import tasks
from eox_nelp.notifications.tasks import send_course_due_date_emails


class SendCourseDueDateEmailtTestCase(unittest.TestCase):
    """Test class for function `send_course_due_date_emails`"""

    def test_send_course_due_date_emails(self):
        """Test when `send_course_due_date_emails` is called
        with the required parameters. Check the functions inside are called with
        their desired values.

        Expected behavior:
            - Log error message.
        """
        log_sent_email = "------Sending upcoming course due date emails.-------"

        with self.assertLogs(tasks.__name__, level="INFO") as logs:
            send_course_due_date_emails()

        self.assertEqual(logs.output, [f"INFO:{tasks.__name__}:{log_sent_email}"])
