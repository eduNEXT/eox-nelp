"""Backend for course_overviews app.

This file contains all the necessary dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/content/course_overviews
"""
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview  # pylint: disable=import-error


def get_course_overview_model():
    """Allow to get CourseOverview model from
    https://github.com/eduNEXT/edunext-platform/blob/master/openedx/core/djangoapps/content/course_overviews/models.py

    Returns:
        CourseOverview model.
    """
    return CourseOverview
