"""
This module contains custom decorators for use in Django views.

Decorators:
    validate_otp(func): A decorator to validate the one-time password (OTP) for a user.
"""
import functools
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework import status

from eox_nelp.utils import save_extrainfo

logger = logging.getLogger(__name__)


def validate_otp(func):
    """
    Decorator to validate the one-time password (OTP) for a user.

    This decorator checks if OTP validation is enabled in the settings. If enabled, it validates the OTP provided
    in the request data against the cached OTP for the user. If the validation fails, it returns an appropriate
    HTTP response. If the validation is successful or if OTP validation is disabled, it calls the wrapped function.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapped function with OTP validation logic applied.

    The wrapped function expects the request data to contain the following fields:
        - phone_number (str): The user's phone number.
        - one_time_password (str): The OTP provided by the user.

    HTTP Responses:
        - 400 Bad Request: If the phone_number or one_time_password is missing from the request data.
        - 403 Forbidden: If the provided OTP does not match the cached OTP for the user.
    """
    @functools.wraps(func)
    def wrapper(request):
        if getattr(settings, "ENABLE_OTP_VALIDATION", True):
            user_phone_number = request.data.get("phone_number", request.user.profile.phone_number)
            proposed_user_otp = request.data.get("one_time_password", None)

            if not user_phone_number or not proposed_user_otp:
                return JsonResponse(
                    data={"detail": "missing phone_number or one_time_password in data."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_otp_key = f"{request.user.username}-{user_phone_number}"
            logger.info("validating otp for %s*****", user_otp_key[:-5])

            if not proposed_user_otp == cache.get(user_otp_key):
                return HttpResponseForbidden(reason="Forbidden - wrong code")

            save_extrainfo(request.user, {"is_phone_validated": True})
            cache.delete(user_otp_key)

        return func(request)

    return wrapper
