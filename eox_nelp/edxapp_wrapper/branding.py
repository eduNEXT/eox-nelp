"""Wrapper for module in branding app.
This contains all the required dependencies from branding.
Attributes:
    get_visible_courses: Wrapper get_visible_courses function.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_BRANDING_BACKEND)

get_visible_courses = backend.get_visible_courses_method()
