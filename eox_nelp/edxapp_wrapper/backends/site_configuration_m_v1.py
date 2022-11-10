"""Backend for site_configuration app.

This file contains all the necessary dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/site_configuration
"""
from openedx.core.djangoapps.site_configuration import helpers  # pylint: disable=import-error


def get_configuration_helpers():
    """Allow to get the module helpers from
    https://github.com/eduNEXT/edunext-platform/blob/master/openedx/core/djangoapps/site_configuration/helpers.py

    Returns:
        helpers module.
    """
    return helpers
