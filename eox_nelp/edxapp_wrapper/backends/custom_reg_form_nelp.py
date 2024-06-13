"""Backend for custom_reg_form special nelp app.

This file contains all the necessary dependencies from extension of the custom_reg_form of nelp.
https://github.com/nelc/nelp-custom-registration-fields
"""
from custom_reg_form.models import ExtraInfo  # pylint: disable=import-error


def get_extra_info_model():
    """Allow to get ExtraInfo model from
    https://github.com/nelc/nelp-custom-registration-fields/blob/main/custom_reg_form/models.py#L8

    Returns:
        ExtraInfo model.
    """
    return ExtraInfo
