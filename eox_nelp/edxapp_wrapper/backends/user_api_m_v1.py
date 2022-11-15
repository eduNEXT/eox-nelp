"""Backend for user_api app.

This file contains all the necessary dependencies from
https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/user_api
"""
from openedx.core.djangoapps.user_api import accounts  # pylint: disable=import-error


def get_accounts():
    """Allow to get the module accounts from
    https://github.com/eduNEXT/edunext-platform/tree/master/openedx/core/djangoapps/user_api/accounts

    Returns:
        accounts module.
    """
    return accounts
