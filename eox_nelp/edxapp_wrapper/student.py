"""Wrapper for modules in common student app.
This contains all the required dependencies from student common app.
Attributes:
    backend:Imported module by using the plugin settings.
    CourseEnrollment: Wrapper CourseEnrollment model.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_STUDENT_BACKEND)

CourseEnrollment = backend.get_course_enrollment_model()
