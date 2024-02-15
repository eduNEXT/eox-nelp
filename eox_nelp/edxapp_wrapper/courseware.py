"""Wrapper courseware.
This contains all the required dependencies from courseware.

Attributes:
    backend: Imported module by using the plugin settings.
    rules: Wrapper of courseware rules.
"""

from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_COURSEWARE_BACKEND)

rules = backend.get_courseware_rules()
