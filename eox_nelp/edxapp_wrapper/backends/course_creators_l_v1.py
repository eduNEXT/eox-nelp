"""Backend for course_creators module.
This file contains all the necessary course_creators dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/cms/djangoapps/course_creators
"""
from cms.djangoapps.course_creators import admin, models  # pylint: disable=import-error


def get_course_creator_model():
    """Allow to get the model CourseCreator from
    https://github.com/eduNEXT/edunext-platform/tree/master/cms/djangoapps/course_creators/models.py
    Returns:
        CourseCreator model.
    """
    return models.CourseCreator


def get_course_creator_admin():
    """Allow to get the openedX CourseCreatorAdmin class.
    https://github.com/eduNEXT/edunext-platform/tree/master/cms/djangoapps/course_creators/admin.py
    Returns:
        CourseCreatorAdmin class.
    """
    return admin.CourseCreatorAdmin
