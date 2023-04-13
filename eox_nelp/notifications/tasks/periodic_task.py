# tasks.py

from celery import shared_task
import logging

@shared_task
def log_message():
    """
    Task to log a message every 5 minutes
    """
    logging.info("This is a log message.")  # Log your desired message here
