"""Notify course date module. This manage the delivery of an
upcoming_course_due_date
"""
import logging

from django.utils import timezone

from eox_nelp.edxapp_wrapper.bulk_email import CourseEmailTemplate, get_course_email_context
from eox_nelp.edxapp_wrapper.student import CourseEnrollment
from eox_nelp.notifications.utils import (
    get_xblock_course_from_usage_key_string,
    get_xblock_from_usage_key_string,
    send_email_multialternative,
)

logger = logging.getLogger(__name__)


def notify_upcoming_course_due_date(upcoming_course_due_date):
    """Send the correspongind email of an UpcomingCourseDate object.
    This is using the bulk-email template that already exists.
    Args:
        upcoming_course_due_date (UpcomingCourseDate): UpcomingCourseDate object to sent emails.
    """
    subsection_key_string = str(upcoming_course_due_date.location_id)
    enrollments_qs = CourseEnrollment.objects.filter(course__id=upcoming_course_due_date.course_id, is_active=True)
    recipient_emails = [enrollment.user.email for enrollment in enrollments_qs if enrollment.user.email]

    subsection_xblock = get_xblock_from_usage_key_string(subsection_key_string)
    course_xblock = get_xblock_course_from_usage_key_string(subsection_key_string)

    if not (subsection_xblock and recipient_emails and course_xblock):
        logger.info(
            "is missing one of the following: subsection-xblock(%s),recipient_emails(%s),course_xblock(%s)",
            subsection_xblock, recipient_emails, course_xblock
        )
        return

    rendered_email_msgs = generate_email_messages(subsection_xblock, course_xblock)
    # to do, add tenant aware settings for context and particular course notification template.

    sent = send_email_multialternative(**rendered_email_msgs, recipient_emails=recipient_emails)

    if sent:
        upcoming_course_due_date.sent = True
        upcoming_course_due_date.save()
        logger.info(
            "%s emails sent related the upcoming_course_due_date: %s -------",
            sent,
            upcoming_course_due_date.__dict__,
        )
    else:
        logger.info(
            "------- No emails were sent!!!, the email function returned %s -------",
            sent,
        )


def generate_email_messages(subsection_xblock, course_xblock):
    """Generate the messages of the email with the data of the subsection and
    course xblock. Return  a dict with the the keys subject, plaintext_msg and html_msg
    of the email to sent.

        Args:
            subsection_xblock (subsectionXblock)
            course_xblock (courseXblock)

        Returns:
            (dict): Dict with the messages rendered of the email.
            It contains: subject, plaintext_msg and html_msg
    """
    email_context = get_course_email_context(course_xblock)
    course_email_template = CourseEmailTemplate.get_template(name='base-notification-template')
    subsection_name = subsection_xblock.display_name
    course_name = course_xblock.display_name
    subsection_due_date = str(subsection_xblock.due)
    delta = subsection_xblock.due - timezone.now()
    time_remaining = (
        f"{delta.days} days, {delta.seconds // 3600:02d} hours, "
        f"and {(delta.seconds // 60) % 60:02d} mins"
    )
    text_message = (
        f"The course {course_name} has a notification. "
        f"The subsection {subsection_name} is coming soon. "
        f"The due date of this subsection is UTC {subsection_due_date}. "
        f"There are approx {time_remaining} for the due date of the subsection."
    )

    html_message = (
        f"<p>The course {course_name} has a notification. "
        f"The subsection {subsection_name} is coming soon.</p>\n"
        f"<p>The due date of this subsection is UTC {subsection_due_date}. "
        f"There are approx {time_remaining} for the due date of the subsection.</p>"
    )

    subject = (
        f"[Futurex platform] Notification due date(left {delta.days} days) of subsection {subsection_name} "
        f"from course {course_name}"
    )
    plaintext_msg = course_email_template.render_plaintext(text_message, email_context)
    html_msg = course_email_template.render_htmltext(html_message, email_context)

    return {
        "subject": subject,
        "plaintext_msg": plaintext_msg,
        "html_msg": html_msg,
    }
