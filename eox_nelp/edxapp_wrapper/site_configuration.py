"""
Wrapper site_configuration app.

This contains all the required dependencies from site_configuration

Attributes:
    backend:Imported site_configuration module by using the plugin settings.
    configuration_helpers: Wrapper helpers module.

"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_SITE_CONFIGURATION)

configuration_helpers = backend.get_configuration_helpers()
