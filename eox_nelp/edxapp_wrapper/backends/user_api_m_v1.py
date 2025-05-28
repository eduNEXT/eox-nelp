"""Backend for user_api app.

This file contains all the necessary dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/user_api
"""
from openedx.core.djangoapps.user_api import accounts, errors, models  # pylint: disable=import-error


def get_accounts():
    """Allow to get the module accounts from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/user_api/accounts

    Returns:
        accounts module.
    """
    return accounts


def get_errors():
    """Allow to get the module errors from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/user_api/errors

    Returns:
        errors module.
    """
    return errors


def get_models():
    """Allow to get the module models from
    https://github.com/nelc/edx-platform/blob/open-release/redwood.nelp/openedx/core/djangoapps/user_api/models.py

    Returns:
        models module.
    """
    return models
