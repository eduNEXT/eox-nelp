"""
Wrapper user_api app.

This contains all the required dependencies from user_api

Attributes:
    backend: Imported user_api module by using the plugin settings.
    accounts: Wrapper accounts module.
    models: Wrapper models module.

"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_USER_API)

accounts = backend.get_accounts()
errors = backend.get_errors()
models = backend.get_models()
