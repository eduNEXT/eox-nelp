"""
Wrapper django_comment_common app.

This contains all the required dependencies from django_comment_common

Attributes:
    backend: Imported django_comment_common module by using the plugin settings.
    comment_client: Wrapper comment_client package.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_DJANGO_COMMENT_COMMON_BACKEND)

comment_client = backend.get_comment_client()
