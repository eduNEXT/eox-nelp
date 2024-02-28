"""
Wrapper user_authn app.

This contains all the required dependencies from user_authn

Attributes:
    backend:Imported user_authn module by using the plugin settings.
    registration_form_factory: Wrapper RegistrationFormFactory class.

"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_USER_AUTHN)

RegistrationFormFactory = backend.get_registration_form_factory()
views = backend.get_views()
