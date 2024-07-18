"""Generic views for NELP one-time-password application.

Function-views:
  - generate_otp: generate and send via SMS the OTP related a user. Saved in cache.

"""
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from eox_nelp.api_clients.sms_vendor import SMSVendorApiClient
from eox_nelp.one_time_password.generators import generate_otp_code
from eox_nelp.one_time_password.view_decorators import validate_otp

logger = logging.getLogger(__name__)


@api_view(["POST"])
@authentication_classes((
    SessionAuthenticationAllowInactiveUser,
))
@permission_classes((IsAuthenticated,))
def generate_otp(request):
    """ View for generate OTP.
    ## Usage

    ### **POST** /eox-nelp/api/one-time-password/v1/generate/

    request example data:
    ``` json
    {
        "phone_number": 3213123123
    }
    ```
    **POST Response Values**
    ``` json
    {
        "message": "Success generate-otp!"
    }
    ```
    """
    user_phone_number = request.data.get("phone_number", request.user.profile.phone_number)

    if not user_phone_number:
        return JsonResponse(
            data={"detail": "missing phone_number in data."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp = generate_otp_code(
        length=getattr(settings, "PHONE_VALIDATION_OTP_LENGTH", 8),
        custom_charset=getattr(settings, "PHONE_VALIDATION_OTP_CHARSET", ""),
    )
    user_otp_key = f"{request.user.username}-{user_phone_number}"
    logger.info("generating otp %s*****", user_otp_key[:-5])
    cache.set(user_otp_key, otp, timeout=getattr(settings, "PHONE_VALIDATION_OTP_TIMEOUT", 600))
    sms_vendor_response = SMSVendorApiClient().send_sms(user_phone_number, f"Futurex Phone Validation Code: {otp}")
    if "error" in sms_vendor_response:
        return JsonResponse(
            data={"detail": "error with SMS Vendor communication"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({"message": "Success generate-otp!"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes((
    SessionAuthenticationAllowInactiveUser,
))
@permission_classes((IsAuthenticated,))
@validate_otp
def validate(request):  # pylint: disable=unused-argument
    """ View for generate OTP.
    ## Usage

    ### **POST** /eox-nelp/api/one-time-password/v1/validate/

    request example data:
    ``` json
    {
        "phone_number": 3213123123,
        "one_time_password": "234fasds"
    }
    ```
    **POST Response Values**
    ``` json
    {
        "message": "Valid OTP code"
    }
    ```
    """
    return Response({"message": "Valid OTP code"}, status=status.HTTP_200_OK)
