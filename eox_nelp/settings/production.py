"""
Settings for eox_nelp project meant to be called on the edx-platform/*/envs/aws.py module
"""
from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ImportError:
    sentry_sdk = DjangoIntegration = None


def plugin_settings(settings):  # pylint: disable=function-redefined
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
