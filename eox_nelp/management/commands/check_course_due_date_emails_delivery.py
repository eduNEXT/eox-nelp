""""Management command to check and if conditions are
stadified, manage the delivery upcoming course due date emails to a celery task."""

import logging

from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):  # lint-amnesty, pylint: disable=too-many-statements
        logger.info('----Checking course due emails by command.-----')
