""""Management command to check and if conditions are
stadified, manage the delivery upcoming course due date emails to a celery task."""

import logging

from django.core.management import BaseCommand

from eox_nelp.notifications.tasks import send_course_due_date_emails


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):  # lint-amnesty, pylint: disable=too-many-statements
        logger.info('----Checking course due emails by command.-----')
