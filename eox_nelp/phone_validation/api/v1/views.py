"""The generic views for NELP OTP to confirm phone number.

function-views:
  - generate_otp: generate and send via SMS the OTP related a user. Saved in cache.
  - validate_otp: Compare and check if the proposed OTP match the User OTP saved in cache.
    If match, updates the profile phone_number.

"""
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from django.http import HttpResponseForbidden, JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response


from eox_nelp.utils import generate_otp_code


logger = logging.getLogger(__name__)


@api_view(["POST"])
def generate_otp(request):
    user_phone_number = request.data.get("phone_number", None)

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
    logger.info(f"generating otp {user_otp_key[:-5]}*****")
    cache.set(user_otp_key, otp, timeout=getattr(settings, "PHONE_VALIDATION_OTP_TIMEOUT", 600))

    return Response({"message": "Success generate-otp!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def validate_otp(request):
    user_phone_number = request.data.get("phone_number", None)
    proposed_user_otp = request.data.get("one_time_password", None)

    if not user_phone_number or not proposed_user_otp:
        return JsonResponse(
            data={"detail": "missing phone_number or one_time_password in data."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_otp_key = f"{request.user.username}-{user_phone_number}"
    logger.info(f"validating otp for {user_otp_key[:-5]}*****")

    if not proposed_user_otp == cache.get(user_otp_key):
        return HttpResponseForbidden(reason="Forbidden - wrong code")

    user = request.user
    user.profile.phone_number = user_phone_number
    user.profile.save()

    return Response({"message": "Success validate-otp!"}, status=status.HTTP_201_CREATED)
