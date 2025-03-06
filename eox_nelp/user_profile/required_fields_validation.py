"""
REQUIRED_USER_FIELDS Configuration

This configuration defines the required fields for different user-related models and their validation rules.
Each field can specify constraints such as character type, format, maximum length, or predefined values.

The `REQUIRED_USER_FIELDS` dictionary is divided into three main categories:

- account: Fields that belong directly to the `User` model (e.g., `user.username`, `user.email`).
- profile: Fields that belong to the `UserProfile` model, accessed via `user.profile.field`
    (e.g., `user.profile.first_name`).
- extra_info: Fields that belong to the `ExtraInfo` model, accessed via `user.extrainfo.field`
    (e.g., `user.extrainfo.arabic_first_name`).

Each category contains specific fields with their respective validation rules.

Allowed `char_type` Values

The `char_type` attribute defines the character set restrictions for each field. Below are the available options:

- latin: Allows only Latin characters (A-Z, a-z) and standard punctuation. Useful for Western languages.
- arabic: Allows only Arabic script characters. Ensures correct encoding for names and texts in Arabic.
- cp1252: Allows characters encoded in Windows-1252 (including accented Latin characters and symbols).
    Common in Western European languages.

Allowed `format` Values

The `format` attribute defines the expected data format for each field. Below are the available options:

- email: Ensures the value is a valid email address.
- phone: Ensures the value is a valid phone number, including the country code.
- date: Requires the value to be a valid date in `YYYY-MM-DD` format.
- numeric: Allows only numeric characters (0-9).

Additional Field Attributes

- max_length: Defines the maximum number of characters allowed for a field. If the value exceeds this limit, it will be
    considered invalid.
- optional_values: Specifies a predefined list of allowed values for a field. Any value outside this list will be
    rejected.
- allow_empty: Indicates whether an empty value is allowed. If set to `False`, an empty value will be considered
    invalid.

Field Category Mapping

The `REQUIRED_USER_FIELDS` dictionary defines the fields that require validation and specifies their attributes.
It is structured as follows:

REQUIRED_USER_FIELDS = {
    "account": {
        "first_name": {"max_length": 30, "char_type": "latin"},
        "last_name": {"max_length": 50, "char_type": "latin"},
    },
    "profile": {
        "city": {"max_length": 32, "char_type": "latin"},
        "country": {"max_length": 2, "optional_values": ["US", "CA", "MX", "BR"]},
        "phone_number": {"max_length": 15, "format": "phone"},
        "mailing_address": {"max_length": 40},
    },
    "extra_info": {
        "arabic_name": {"max_length": 20, "char_type": "arabic"},
        "arabic_first_name": {"max_length": 20, "char_type": "arabic"},
        "arabic_last_name": {"max_length": 50, "char_type": "arabic"},
    },
}
"""
import logging

from custom_reg_form.models import ExtraInfo
from django.conf import settings

from eox_nelp.validators import validate_char_type, validate_format, validate_max_length, validate_optional_values

logger = logging.getLogger(__name__)


def validate_required_user_fields(user):
    """
    Validates the required fields of a user instance based on the REQUIRED_USER_FIELDS setting.

    This function checks the user's account, profile, and extra_info fields to ensure they comply with the validation
    rules defined in the settings. If a field is missing or contains invalid data, it is added to the output dictionary
    under its respective category.

    Args:
        user (User): The user instance to validate.

    Returns:
        dict: A dictionary containing invalid fields categorized by "account", "profile", and "extra_info".
              Each field will have an empty list if valid, or a list of error messages if invalid.

    Example:
        Given the following REQUIRED_USER_FIELDS setting:

        REQUIRED_USER_FIELDS = {
            "account": {"first_name": {"max_length": 30}, "last_name": {"max_length": 50}},
            "profile": {
                "city": {"max_length": 32},
                "country": {"max_length": 2},
                "phone_number": {"format": "phone"},
                "mailing_address": {"max_length": 40},
            },
            "extra_info": {
                "arabic_name": {"char_type": "arabic"},
                "arabic_first_name": {"char_type": "arabic"},
                "arabic_last_name": {"char_type": "arabic"},
            },
        }

        A possible output from this function could be:

        {
            "account": {"first_name": ["An error"], "last_name": []},
            "profile": {"city": [], "country": [], "phone_number": ["Empty field"], "mailing_address": []},
            "extra_info": {"arabic_name": [], "arabic_first_name": [], "arabic_last_name": []}
        }
    """
    required_fields_config = getattr(settings, "REQUIRED_USER_FIELDS", {})

    account_fields = required_fields_config.get("account", {})
    profile_fields = required_fields_config.get("profile", {})
    extra_info_fields = required_fields_config.get("extra_info", {})

    return {
        "account": validate_account_fields(user, account_fields),
        "profile": validate_profile_fields(user, profile_fields),
        "extra_info": validate_extra_info_fields(user, extra_info_fields),
    }


def validate_account_fields(user, account_fields):
    """
    Validates the account fields of the user.

    Args:
        user (User): The user instance.
        account_fields (dict): Dictionary of required fields and their validation rules.

    Returns:
        dict: A dictionary with invalid account fields and their errors.
    """
    return validate_user_fields(user, account_fields)


def validate_profile_fields(user, profile_fields):
    """
    Validates the profile fields of the user.

    Args:
        user (User): The user instance.
        profile_fields (dict): Dictionary of required fields and their validation rules.

    Returns:
        dict: A dictionary with invalid profile fields and their errors.
    """
    return validate_user_fields(getattr(user, "profile", None), profile_fields)


def validate_extra_info_fields(user, extra_info_fields):
    """
    Validates the extra_info fields of the user.

    Args:
        user (User): The user instance.
        extra_info_fields (dict): Dictionary of required fields and their validation rules.

    Returns:
        dict: A dictionary with invalid extra_info fields and their errors.
    """
    # pylint: disable=no-member
    try:
        extra_info = ExtraInfo.objects.get(user=user)
    except ExtraInfo.DoesNotExist:
        return {field: ["Empty field"] for field in extra_info_fields.keys() if hasattr(ExtraInfo, field)}

    return validate_user_fields(extra_info, extra_info_fields)


def validate_user_fields(instance, fields):
    """
    Generic function to validate fields for a given user instance.

    Args:
        instance (object): The model instance (user, user.profile, user.extrainfo).
        fields (dict): Dictionary of required fields and their validation rules.

    Returns:
        dict: A dictionary with invalid fields and their errors.
    """
    result = {}

    if not instance:
        return result

    for field, rules in fields.items():
        if not hasattr(instance, field):
            logger.warning("Invalid configuration for %s field", field)
            continue

        value = getattr(instance, field)
        errors = validate_field(value, rules)
        result[field] = errors

    return result


def validate_field(value, rules):
    """
    Validates a field based on its rules.

    Args:
        value (str): The field value to validate.
        rules (dict): The validation rules.

    Returns:
        list: A list of validation error messages. Empty if valid.
    """
    if not value and not rules.get("allow_empty", False):
        return ["Empty field"]

    if not value:
        # This is required since validation supports str fields and None value are not allowed
        value = ""

    errors = []

    validators = {
        "max_length": validate_max_length,
        "char_type": validate_char_type,
        "format": validate_format,
        "optional_values": validate_optional_values,
    }

    for rule, argument in rules.items():
        validator = validators.get(rule)

        if validator and not validator(value, argument):
            errors.append(f"{rule} with argument {argument} failed")

    return errors
