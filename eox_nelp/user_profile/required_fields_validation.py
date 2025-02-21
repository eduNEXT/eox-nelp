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
import re

from django.conf import settings
from phonenumber_field.phonenumber import PhoneNumber

logger = logging.getLogger(__name__)


def validate_required_user_fields(user):
    """
    Validates user fields and returns a dictionary with invalid fields categorized by account, profile, and extra_info.
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
    return validate_user_fields(getattr(user, "extrainfo", None), extra_info_fields)


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

        if not value:
            errors = ["Empty field"]
        else:
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


def validate_max_length(value, max_length):
    """
    Checks if the given value does not exceed the specified max_length.

    Args:
        value (str): The value to be validated.
        max_length (int): The maximum allowed length.

    Returns:
        bool: True if valid, False if it exceeds max_length.
    """
    return len(str(value)) <= max_length


def validate_optional_values(value, allowed_values):
    """
    Checks if the given value is within the predefined allowed values.

    Args:
        value (str): The value to be validated.
        allowed_values (list): A list of allowed values.

    Returns:
        bool: True if the value is in the allowed list, False otherwise.
    """
    return value in allowed_values


def validate_char_type(value, char_type):
    """
    Validates if the given value matches the specified character type.

    Args:
        value (str): The value to be validated.
        char_type (str): The character type to validate against. Options: "latin", "arabic", "cp1252".

    Returns:
        bool: True if the value matches the specified character type, False otherwise.
    """
    validators = {
        "latin": validate_latin,
        "arabic": validate_arabic,
        "cp1252": validate_cp1252,
    }

    validator = validators.get(char_type)

    if validator:
        return validator(value)

    return False


def validate_latin(value):
    """
    Checks if the given value contains only Latin characters and standard punctuation.

    Args:
        value (str): The value to be validated.

    Returns:
        bool: True if valid, False otherwise.
    """
    latin_regex = r'^[a-zA-ZÀ-ÿ\s.,\'"-]*$'
    return re.match(latin_regex, value) is not None


def validate_arabic(value):
    """
    Checks if the given value contains only Arabic script characters.

    Args:
        value (str): The value to be validated.

    Returns:
        bool: True if valid, False otherwise.
    """
    arabic_regex = r'^[\u0600-\u06FF\s]+$'  # Unicode range for Arabic characters
    return re.match(arabic_regex, value) is not None


def validate_cp1252(value):
    """
    Checks if the given value contains only Windows-1252 compatible characters.

    Args:
        value (str): The value to be validated.

    Returns:
        bool: True if valid, False otherwise.
    """
    cp1252_regex = r'^[\x00-\x7F\x80-\x9F\xA0-\xFF]*$'
    return re.match(cp1252_regex, value) is not None


def validate_format(value, field_format):
    """
    Validates if the given value matches the specified format.

    Args:
        value (str): The value to be validated.
        field_format (str): The format to validate against. Options: "email", "phone", "numeric", "alphanumeric".

    Returns:
        bool: True if the value matches the specified format, False otherwise.
    """
    validators = {
        "email": validate_email,
        "phone": validate_phone,
        "numeric": validate_numeric,
    }

    validator = validators.get(field_format)

    if validator:
        return validator(value)

    return False


def validate_email(value):
    """
    Checks if the given value is a valid email address.

    Args:
        value (str): The value to be validated.

    Returns:
        bool: True if valid, False otherwise.
    """
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, value) is not None


def validate_phone(value):
    """
    Checks if the given value is a valid phone number using django-phonenumber-field.

    Args:
        value (str): The phone number to be validated.

    Returns:
        bool: True if valid, False otherwise.
    """
    phone = PhoneNumber.from_string(value)

    return phone.is_valid()


def validate_numeric(value):
    """
    Checks if the given value contains only numeric digits.

    Args:
        value (str): The value to be validated.

    Returns:
        bool: True if valid, False otherwise.
    """
    return value.isdigit()
