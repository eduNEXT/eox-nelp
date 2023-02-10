"""
Wrapper course_api app.

This contains all the required dependencies from course_api.
Attributes:
    backend:Imported module by using the plugin settings.
    CourseDetailSerializer: Serilizer to add extra chantes..
    CourseDetailView: Wrapper CourseDetailView class.
    CourseListView: Wrapper CourseListDetailView class
"""
from importlib import import_module

from django.conf import settings


backend = import_module(settings.EOX_NELP_COURSE_API)

CourseDetailSerializer = backend.get_course_detail_serializer()

CourseDetailView = backend.get_course_detail_view()

CourseListView = backend.get_course_list_view()
