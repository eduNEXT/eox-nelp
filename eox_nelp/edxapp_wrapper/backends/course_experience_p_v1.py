"""Backend for course_experience module.
This file contains all the necessary course_experience dependencies from
https://github.com/openedx/edx-platform/blob/open-release/palm.master/openedx/features/course_experience/
"""
from openedx.features.course_experience import course_home_url  # pylint: disable=import-error


def get_course_home_url():
    """Allow to get the course_home_url function from
    https://github.com/openedx/edx-platform/blob/open-release/palm.master/openedx/features/course_experience/__init__.py
        Returns:
        course_home_url function.
    """
    return course_home_url
