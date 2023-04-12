"""Backend for bulk_email django app module.
This file contains all the necessary bulk_email dependencies from
https://github.com/eduNEXT/edunext-platform/tree/ednx-release/mango.master/lms/djangoapps/bulk_email"""
from lms.djangoapps.bulk_email.models import CourseEmailTemplate  # pylint: disable=import-error
from lms.djangoapps.bulk_email.tasks import _get_course_email_context  # pylint: disable=import-error


def get_course_email_template_model():
    """Allow to get the CourseEmailTemplate Model from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/bulk_email/models.py#L343
    Returns:
        CourseEmailTemplate Model.
    """
    return CourseEmailTemplate


def get_course_email_context_method():
    """Allow to get the model CourseDetailView from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/bulk_email/tasks.py#L101
    Returns:
        get_course_email_context_ view.
    """
    return _get_course_email_context
