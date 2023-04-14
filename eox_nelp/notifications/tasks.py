# tasks.py

from celery import shared_task
import logging
logger = logging.getLogger(__name__)

@shared_task
def log_message():
    """
    Task to log a message every 5 minutes
    """
    logger.info("This is a log message.")  # Log your desired message here
