"""Custom NELP  authentication pipelines

functions:
    social_details: Allows to map response fields to user standard fields.
    invalidate_current_user: Sets to None the current user.
"""
from django.conf import settings
from django.contrib.auth import logout
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


def invalidate_current_user(request, *args, user=None, **kwargs):  # pylint: disable=unused-argument
    """This pipeline sets to None the current user in order to avoid invalid associations.

    This was implemented due to an unexpected behavior when a user is logged and a different
    user tries to authenticate by using a SAML IDP in the same browser, the result is that
    instead of having two different accounts the second user is associated to the first user's
    account, this behavior is the result of SESSION_COOKIE_SAMESITE = "None" however the
    possible fix, SESSION_COOKIE_SAMESITE = "Lax", has not been tested in the whole platform
    therefore that can not be implemented yet.

    **NOTE**
        * This MUST be the first pipeline.
        * This just has been tested in the NELP environment where the linked accounts feature
         was deactivated.
    """
    if user:
        logout(request)

        return {
            "user": None
        }

    return {}
