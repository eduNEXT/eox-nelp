"""Backend for course_blocks django app module.
This file contains all the necessary course_blocks dependencies from
https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/course_blocks/__init__.py"""
from lms.djangoapps.course_blocks.utils import get_student_module_as_dict


def get_student_module_as_dict_method():
    """Allow to get the get_visible_courses function from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/course_blocks/__init__.py#L17
    Returns:
        get_visible_courses function.
    """
    return get_student_module_as_dict
