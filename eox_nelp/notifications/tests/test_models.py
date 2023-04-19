"""This file contains all the test for notifications/models.py file.

Classes:
    UpcomingCourseDueDateTestCase: Test UpcomingCourseDueDate django model.
"""
import unittest

from django.utils import timezone

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.notifications import models
from eox_nelp.notifications.models import UpcomingCourseDueDate


class UpcomingCourseDueDateTestCase(unittest.TestCase):
    """Test class for model UpcomingCourseDueDate"""

    def test_nofity_log(self):
        """Test that the notify model logs progress message.

        Expected behavior:
            - Log progress message successfully.
        """
        instance, _ = UpcomingCourseDueDate.objects.get_or_create(  # pylint: disable=no-member
            course=CourseOverview.objects.create(id="course-v1:test+Cx105+2022_T4"),
            location_id="block-v1:test+CS501+2022_T4+type@sequential+block@a54730a9b89f420a8d0343dd581b447a",
            due_date=timezone.now(),
            notification_date=timezone.now(),
        )
        processing_log = f"Processing notification for UpcomingCourseDueDate with id {instance.id}"

        with self.assertLogs(models.__name__, level="INFO") as logs:
            instance.notify()

        self.assertEqual(logs.output, [f"INFO:{models.__name__}:{processing_log}"])
