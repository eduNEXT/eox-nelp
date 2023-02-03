"""
Wrapper mfe_config api view.

This contains  the required api view from mfe_config

Attributes:
    backend:Imported site_configuration module by using the plugin settings.
    MFEConfigView: Wrapper mfe_config  api view class.
"""
from importlib import import_module

from django.conf import settings

mfe_config_view = import_module(settings.EOX_NELP_MFE_CONFIG_VIEW)

MFEConfigView = mfe_config_view.get_MFE_config_view()
