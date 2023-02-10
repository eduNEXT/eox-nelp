"""
Settings for eox_nelp project meant to be called on the edx-platform/*/envs/devstack.py module
"""
from .production import *  # pylint: disable=wildcard-import, unused-wildcard-import  # noqa: F401


def plugin_settings(settings):  # pylint: disable=function-redefined, unused-argument
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
