"""Notification tasks. Contains all tasks related with the notifications features.

tasks:
    create_course_notifications: Creates UpcomingCourseDueDate records based on due dates.
"""
import datetime

from celery import shared_task
from django.utils import timezone
from opaque_keys.edx.keys import CourseKey

from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.notifications.models import UpcomingCourseDueDate


@shared_task
def create_course_notifications(course_id):
    """Creates UpcomingCourseDueDate records based on due dates. This considers the following rules:

        1. The course must have the notification feature active, add the following dict to other_course_settings
           to do that.

            {
                "notifications": {
                    "active": true,
                    "days_in_advance": [
                        1,
                        2,
                        3
                    ]
                }
            }

        2. If days_in_advance is not set, the default value will be [7]
        3. If the subsection doesn't have a due date, nothing will happen.
        4. If the subsection already has UpcomingCourseDuedates records and they has not been sent, they will be
           deleted.
        5. If the subsection already has UpcomingCourseDuedates records and they has been sent, this will preserve
           that data to keep a register.
        6. If the notification date is in the past, the record won't be created.

    Args:
        course_id (str): Unique course identifier.
    """
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)

    notifications = course.other_course_settings.get("notifications", {})

    if not notifications.get("active"):
        return

    now = timezone.now()
    days_in_advance = notifications.get("days_in_advance")

    if not days_in_advance:
        days_in_advance = [7]

    if not isinstance(days_in_advance, list):
        days_in_advance = [days_in_advance]

    sub_sections = modulestore().get_items(course_key, qualifiers={"category": "sequential"})

    for sub_section in sub_sections:
        created_or_updated = []
        due_date = sub_section.due

        if not due_date:
            continue

        for day in days_in_advance:
            notification_date = due_date - datetime.timedelta(days=int(day))

            if notification_date < now:
                continue

            obj, _ = UpcomingCourseDueDate.objects.update_or_create(  # pylint: disable=no-member
                course_id=course_id,
                location_id=sub_section.location,
                notification_date=notification_date,
                defaults={"due_date": due_date, "notification_date": notification_date},
            )
            created_or_updated.append(obj.id)

        UpcomingCourseDueDate.objects.exclude(id__in=created_or_updated).filter(  # pylint: disable=no-member
            course_id=course_id,
            location_id=sub_section.location,
            sent=False,
        ).delete()
