"""Wrapper custom_reg_form module file.
This contains all the required dependencies from custom_reg_form.

Attributes:
    backend:Imported module by using the plugin settings.
    ExtraInfo: Wrapper ExtraInfo model.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_CUSTOM_REG_FORM_BACKEND)

ExtraInfo = backend.get_extra_info_model()
