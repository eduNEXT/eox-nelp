"""Backend for mfe_config view.

This file contains all the necessary dependencies from
https://github.com/edx/edx-platform/tree/master/lms/djangoapps/mfe_config_api
"""
from lms.djangoapps.mfe_config_api.views import MFEConfigView


def get_MFE_config_view():
    """Allow to get the mfe_config view class  from
    https://github.com/edx/edx-platform/tree/master/lms/djangoapps/mfe_config_api/views.py

    Returns:
        helpers module.
    """
    return MFEConfigView
