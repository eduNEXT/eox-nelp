"""
This module provides helper functions for managing user-related operations
that extend beyond the default behavior of Open edX account serializers.

It encapsulates logic for updating core user attributes and handling additional
profile information required by specific platform features or customization layers.

These utilities are intended to centralize user update logic, promote reusability,
and maintain clean separation between views and business logic.
"""
from django.conf import settings
from django.utils.translation import gettext as _

from eox_nelp.edxapp_wrapper.user_api import accounts, errors
from eox_nelp.utils import save_extrainfo
from eox_nelp.validators import validate_phone


def update_account(user, data):
    """
    Updates core user account fields based on the request data.

    This function:
    - Optionally validates the phone number format if the setting USER_PROFILE_API_VALIDATE_PHONE_NUMBER is True.
    - Calls update_account_settings to update supported fields.
    - Manually updates additional fields (e.g., first_name, last_name) defined in EXTRA_ACCOUNT_USER_FIELDS
      that are not handled by the standard serializers.

    Args:
        user (User): The Django user instance whose data will be updated.
        data (dict): Dictionary containing the fields and values to be updated.

    Raises:
        AccountValidationError: If phone number validation fails.
    """
    validate_phone_number = getattr(settings, 'USER_PROFILE_API_VALIDATE_PHONE_NUMBER', False)
    phone_number = data.get("phone_number")

    if validate_phone_number and phone_number and not validate_phone(phone_number):
        raise errors.AccountValidationError({"phone_number": [_("Invalid phone number")]})

    accounts.api.update_account_settings(user, data)

    # This extra code block is required since the method update_account_settings just
    # allows to update fields defined in the AccountUserSerializer and the AccountLegacyProfileSerializer
    # so some fields like first_name and last_name are not editable in the standad implementation.

    extra_account_user_fields = getattr(settings, "EXTRA_ACCOUNT_USER_FIELDS", [])

    for field in extra_account_user_fields:
        if (value := data.get(field)) and hasattr(user, field):
            setattr(user, field, value)
            user.save()


def update_extrainfo(user, data):
    """
    Updates user-related extra information fields not handled by the standard account serializers.

    This function:
    - Retrieves a list of extra info fields from USER_PROFILE_API_EXTRA_INFO_FIELDS setting.
    - Extracts matching fields from the request data.
    - Persists the data using save_extrainfo helper.

    Fields are saved only if they are present in the request.

    Args:
        user (User): The Django user instance whose extra info will be updated.
        data (dict): Dictionary containing the extra info fields and values to be updated.
    """
    required_user_extra_info_fields = getattr(settings, 'USER_PROFILE_API_EXTRA_INFO_FIELDS', [])
    extra_info_data = {
        field: data[field] for field in required_user_extra_info_fields if field in data
    }

    if extra_info_data:
        save_extrainfo(user, extra_info_data)
