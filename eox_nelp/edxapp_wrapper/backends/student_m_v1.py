"""Backend for student django app module.
This file contains all the necessary student dependencies from
https://github.com/eduNEXT/edunext-platform/tree/ednx-release/mango.master/common/djangoapps/student
"""
from common.djangoapps.student.models import CourseEnrollment  # pylint: disable=import-error


def get_course_enrollment_model():
    """Allow to get the CourseEnrollment Model from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/common/djangoapps/student/models.py#L1234
    Returns:
        CourseEnrollment Model.
    """
    return CourseEnrollment