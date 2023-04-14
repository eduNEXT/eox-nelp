""""Management command to send upcoming course due date emails."""

import logging

from django.core.management import BaseCommand

from eox_nelp.notifications.tasks import send_upcoming_course_due_date_emails


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):  # lint-amnesty, pylint: disable=too-many-statements
        logger.info('Sending periodic course due emails by command.')
        send_upcoming_course_due_date_emails.delay()
