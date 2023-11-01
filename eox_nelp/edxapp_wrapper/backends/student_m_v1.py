"""Backend for student django app module.
This file contains all the necessary student dependencies from
https://github.com/eduNEXT/edunext-platform/tree/ednx-release/mango.master/common/djangoapps/student
"""
from common.djangoapps.student import roles
from common.djangoapps.student.models import (  # pylint: disable=import-error
    CourseAccessRole,
    CourseEnrollment,
    UserProfile,
)


def get_course_enrollment_model():
    """Allow to get the CourseEnrollment Model from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/common/djangoapps/student/models.py#L1234
    Returns:
        CourseEnrollment Model.
    """
    return CourseEnrollment


def get_course_access_role_model():
    """Allow to get the CourseAccessRole Model from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/common/djangoapps/student/models.py#L2554
    Returns:
        CourseAccessRole Model.
    """
    return CourseAccessRole


def get_user_profile_model():
    """Allow to get the UserProfile Model from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/common/djangoapps/student/models.py#L478
    Returns:
        UserProfile Model.
    """
    return UserProfile


def get_student_roles():
    """Allow to get the Roles Module file  from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master.nelp/common/djangoapps/student/roles.py
    Returns:
        Roles module.
    """
    return roles
