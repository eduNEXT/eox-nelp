"""Notifications models. This contains all models related with the notification.

Models:
    UpcomingCourseDueDate: Model that sends notifications based on the subsection stored data.
"""
import logging
from importlib import import_module

from django.db import models
from opaque_keys.edx.django.models import UsageKeyField

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

LOGGER = logging.getLogger(__name__)


class UpcomingCourseDueDate(models.Model):
    """Django model that stores necessary data to send email notifications to enrolled
    users.

    Fields:
        course_id<Foreignkey>: Reference to a specific course.
        location_id<UsageKeyField>: Store subsection id.
        due_date<DateTimeField>: Subsection due date.
        notification_date<DateTimeField>: Date when the notification must be sent.
        sent<BooleanField>: Indicates if the notification was already sent.
    """
    course = models.ForeignKey(CourseOverview, null=False, on_delete=models.CASCADE)
    location_id = UsageKeyField(max_length=255, null=False)
    due_date = models.DateTimeField(null=False)
    notification_date = models.DateTimeField(null=False)
    sent = models.BooleanField(default=False)

    class Meta:
        """
        Set model constrains; course_id, location_id and notification_date
        combination must be unique to avoit duplicates.
        """
        unique_together = [["course_id", "location_id", "notification_date"]]

    def notify(self):
        """Send email remainders to enrolled users."""
        LOGGER.info(
            "Processing notification for UpcomingCourseDueDate with id %s",
            self.id,  # pylint: disable=no-member
        )
        import_module("eox_nelp.notifications.tasks").notify_upcoming_course_due_date_by_id.delay(
            self.id,  # pylint: disable=no-member
        )
