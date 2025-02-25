""""Management command to check course due dates. If conditions are
satisfied, manage the delivery with notify method of the UpcomingCourseDueDate object.
To run it use:
`./manage lms notify_course_due_dates`.
"""

import logging

from django.core.management import BaseCommand
from django.utils import timezone

from eox_nelp.notifications.models import UpcomingCourseDueDate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Class command to check course due dates and also notify the corresponding."""
    def handle(self, *args, **options):  # lint-amnesty

        logger.info('----Checking course due dates emails by command.-----')
        now = timezone.now()
        delivery_qs = UpcomingCourseDueDate.objects.filter(  # pylint: disable=no-member
            notification_date__lte=now,
            due_date__gte=now,
            sent=False,
        )

        for upcoming_course_due_date in delivery_qs:
            upcoming_course_due_date.notify()
