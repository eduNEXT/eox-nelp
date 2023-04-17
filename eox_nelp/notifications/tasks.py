"""
Celery task related the notifications eox-nelp module.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_course_due_date_emails():
    """
    Task to send upcoming course due date emails.
    """
    logger.info("------Sending upcoming course due date emails.-------")
