"""Custom NELP  authentication pipelines

functions:
    social_details: Allows to map response fields to user standard fields.
    invalidate_current_user: Sets to None the current user.
"""
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from social_core.pipeline.social_auth import social_details as social_core_details

from eox_nelp.edxapp_wrapper.edxmako import edxmako


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


def invalidate_current_user(*args, user=None, **kwargs):  # pylint: disable=unused-argument
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
        return {
            "user": None
        }

    return {}


def close_mismatch_session(request, *args, user=None, **kwargs):  # pylint: disable=unused-argument
    """This pipeline closes the current session if the pipeline user doesn't match with the session user.

    This ensures that the browser session will show the right account, when a user tries to authenticate
    in a device that has a logged account.
    """
    if request.user != user:
        logout(request)

    return {}


def safer_associate_username_by_uid(  # pylint: disable=unused-argument
    request, backend, details, response, *args, user=None, **kwargs,
):
    """Pipeline to retrieve user if possible matching uid with the username of a user.
    The uid is based in the configuration of the saml with the field `attr_user_permanent_id`:
    https://github.com/python-social-auth/social-core/blob/master/social_core/backends/saml.py#L49

    This is using the idp and the uid inspired in:
    https://github.com/python-social-auth/social-core/blob/master/social_core/backends/saml.py#L296C23-L297
    Raises:
        EoxNelpAuthException: If someone tries to have staff or superuser permission using tpa.

    Returns:
        dict: Dict with user if matches, if not return None.
    """
    if user:
        return None

    idp = backend.get_idp(response["idp_name"])
    uid = idp.get_user_permanent_id(response["attributes"])
    user_match = backend.strategy.storage.user.get_user(username=uid)

    if not user_match:
        return None
    if user_match.is_staff or user_match.is_superuser:
        return HttpResponseForbidden(
            edxmako.shortcuts.render_to_string(
                "static_templates/server-error.html",
                {
                    "page_header": _("It is not allowed to auto associate staff or admin users"),
                    "page_content": _(
                        "You are trying to access with a user that already exists with privileged permissions."
                        " Please try to authenticate on the site where you registered for the first time "
                        "or contact support to change permissions."
                    ),
                },
                request=request,
            )
        )
    return {
        "user": user_match,
        "is_new": False,
    }
