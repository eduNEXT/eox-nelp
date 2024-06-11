"""Generic views for NELP user's profile application.

Function-views:
  - generate_otp: generate and send via SMS the OTP related a user. Saved in cache.
  - validate_otp: Compare and check if the proposed OTP match the User OTP saved in cache.
    If match, updates the profile phone_number.

"""
import logging

from django.db import transaction
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from eox_nelp.edxapp_wrapper.user_api import accounts, errors
from eox_nelp.one_time_password.view_decorators import validate_otp

logger = logging.getLogger(__name__)


@api_view(["POST"])
@authentication_classes((
    SessionAuthenticationAllowInactiveUser,
))
@permission_classes((IsAuthenticated,))
@validate_otp
def update_user_data(request):
    """ View to update user's fields.
    ## Usage

    ### **POST** /eox-nelp/api/user-profile/v1/update-user-data/

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
        "message": "User's fields has been updated successfully"
    }
    ```
    """
    try:
        with transaction.atomic():
            accounts.api.update_account_settings(request.user, request.data)
    except errors.AccountValidationError as err:
        return Response({"field_errors": err.field_errors}, status=status.HTTP_400_BAD_REQUEST)
    except errors.AccountUpdateError as err:
        return Response(
            {
                "developer_message": err.developer_message,
                "user_message": err.user_message
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"message": "User's fields has been updated successfully"}, status=status.HTTP_200_OK)
