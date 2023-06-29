"""Backend for branding django app module.
This file contains all the necessary branding dependencies from
https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/branding/__init__.py"""
from lms.djangoapps.branding import get_visible_courses


def get_visible_courses_method():
    """Allow to get the get_visible_courses function from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/branding/__init__.py#L17
    Returns:
        get_visible_courses function.
    """
    return get_visible_courses
