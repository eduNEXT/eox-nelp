"""Notification utils"""
import logging

from django.core.mail import EmailMultiAlternatives
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import UsageKey

from eox_nelp.edxapp_wrapper.modulestore import ItemNotFoundError, modulestore

logger = logging.getLogger(__name__)


def send_email_multialternative(
    subject=None,
    plaintext_msg=None,
    html_msg=None,
    recipient_emails=None,
    from_email=None,
):
    """
    Function to send emails with plaintext msg and html msg.
    Returns:
        (int): Number of emails sent.
    """
    logger.info("------Sending email with subject: %s -------", subject)
    msg = EmailMultiAlternatives(subject, plaintext_msg, from_email, recipient_emails)
    msg.attach_alternative(html_msg, "text/html")
    return msg.send()


def get_xblock_from_usage_key_string(usage_key_string):
    """Get the object xblock  represetation of a usage_key string from modulestore.

    Args:
        usage_key_string (str): Usage key in string representation.

    Returns:
        xblock: xblock of usage key object. If not found return None.
    """
    try:
        usage_key = UsageKey.from_string(usage_key_string)

        return modulestore().get_item(usage_key, depth=None)
    except (InvalidKeyError, ItemNotFoundError):
        return None


def get_xblock_course_from_usage_key_string(usage_key_string):
    """Get the  course xblock  represetation of a usage_key string from modulestore.

    Args:
        usage_key_string (str): Usage key in string representation.

    Returns:
        xblock_course: xblock of courses object. If not found return None.
    """
    try:
        usage_key = UsageKey.from_string(usage_key_string)

        return modulestore().get_course(usage_key.course_key, depth=None)
    except InvalidKeyError:
        return None
