"""Backend for course_api django app module.
This file contains all the necessary course_creators dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/course_api
"""
from lms.djangoapps.course_api import serializers, views  # pylint: disable=import-error


def get_course_detail_serializer():
    """Allow to get the serializes CourseDetailSerializer from
    https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/course_api/serializers.py
    Returns:
        CourseDetailSerializer serializer.
    """
    return serializers.CourseDetailSerializer


def get_course_detail_view():
    """Allow to get the model CourseDetailView from
    https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/course_api/views.py
    Returns:
        CourseDetailView view.
    """
    return views.CourseDetailView


def get_course_list_view():
    """Allow to get the view CourseListView from
    https://github.com/eduNEXT/edunext-platform/tree/master/lms/djangoapps/course_api/views.py
    Returns:
        CourseListView view.
    """
    return views.CourseListView
