"""Wrapper instructor.
This contains all the required dependencies from instructor.

Attributes:
    backend: Imported module by using the plugin settings.
    rules: Wrapper of courseware rules.
"""

from importlib import import_module

from django.conf import settings


backend = import_module(settings.EOX_NELP_INSTRUCTOR_BACKEND)

permissions = backend.get_instructor_permissions()
