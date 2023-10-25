"""Backend for cms api v1 views.

This file contains all the necessary dependencies from
https://github.com/openedx/edx-platform/blob/open-release/maple.master/cms/djangoapps/api/v1/views/course_runs.py
"""
from cms.djangoapps.api.v1.views.course_runs import CourseRunViewSet


def get_course_runs_view():
    """Allow to get the course runs cms view class  from
    https://github.com/openedx/edx-platform/blob/open-release/maple.master/cms/djangoapps/api/v1/views/course_runs.py

    Returns:
        CourseRunViewSet view.
    """
    return CourseRunViewSet
