"""Custom NELP  authentication pipelines

functions:
    social_details: Allows to map response fields to user standar fields.
"""
from django.conf import settings
from social_core.pipeline.social_auth import social_details as social_core_details


def social_details(backend, details, response, *args, **kwargs):
    """This is an extension of `social_core.pipeline.social_auth.social_details` that allows
    to map response fields in standard user fields. This depends on the SOCIAL_DETAILS_MAPPING
    setting that should be configured as the following:

    Example:

        SOCIAL_DETAILS_MAPPING = {
            "username": "custom_username_response_value",
            "email": "custom_email_response_value",
            "first_name": "custom_first_name_response_value",
            "last_name": "custom_last_name_response_value",
            "fullname": "custom_fullname_response_value"
        }
    """
    details = social_core_details(backend, details, response, *args, **kwargs)

    for key, value in getattr(settings, "SOCIAL_DETAILS_MAPPING", {}).items():
        details["details"][key] = response.get(value)

    return details
