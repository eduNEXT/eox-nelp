"""Wrapper course_experience.
This contains all the required dependencies from course_experience.

Attributes:
    backend: Imported module by using the plugin settings.
    course_experience: Module for openedx course_experience
"""

from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_COURSE_EXPERIENCE_BACKEND)

course_home_url = backend.get_course_home_url()
