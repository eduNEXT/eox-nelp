"""Wrapper for event-routing-backends library.

This contains all the required dependencies from event-routing-backends.

Attributes:
    constants: Wrapper constants module.
    XApiTransformer: Wrapper for the XApiTransformer class.
    XApiTransformersRegistry: Wrapper for the XApiTransformersRegistry class.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_EVENT_ROUTING_BACKEND)

constants = backend.get_xapi_constants()
XApiTransformer = backend.get_xapi_transformer()
XApiTransformersRegistry = backend.get_xapi_transformer_registry()
