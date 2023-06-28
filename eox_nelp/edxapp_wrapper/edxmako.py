"""
Wrapper edxmako module.

This contains all the required dependencies from modulestore

Attributes:
    backend:Imported module by using the plugin settings.
    edxmako: Wrapper edxmako module.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_EDXMAKO_BACKEND)

edxmako = backend.get_edxmako()
