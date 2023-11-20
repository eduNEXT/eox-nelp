"""Wrapper course_overviews module file.
This contains all the required dependencies from course_overviews.

Attributes:
    backend:Imported module by using the plugin settings.
    CourseOverview: Wrapper CourseOverview model.
    get_course_overviews: Wrapper of et_course_overviews method.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_COURSE_OVERVIEWS_BACKEND)

CourseOverview = backend.get_course_overview_model()
get_course_overviews = backend.get_course_overviews_method()
