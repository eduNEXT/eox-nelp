"""Wrapper for module in bulk email app.
This contains all the required dependencies from course_creators.
Attributes:
    backend:Imported module by using the plugin settings.
    CourseEmailTemplate: Wrapper CourseEmailTemplate model.
    get_course_email_context: Wrapper get_course_email_context function.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_BULK_EMAIL_BACKEND)

CourseEmailTemplate = backend.get_course_email_template_model()
get_course_email_context = backend.get_course_email_context_method()
