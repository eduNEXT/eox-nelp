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
- dependent_fields: Specifies conditions where the validity of a field depends on the value of another field.
    This is useful for cases where a field's allowed values change based on another related field.

### `dependent_fields` Usage

The `dependent_fields` attribute is used when a field's valid values are conditional on another field’s value.
For example, the `city` field in the `profile` category may depend on the `country` field:

"profile": {
    "city": {
        "max_length": 32,
        "char_type": "latin",
        "dependent_fields": {
            "profile.country": {
                "CO": ["Bogota", "Medellin", "Cali"],
                "US": "Florida"
            }
        }
    },
}

Field Category Mapping

The `REQUIRED_USER_FIELDS` dictionary defines the fields that require validation and specifies their attributes.
It is structured as follows:

REQUIRED_USER_FIELDS = {
    "account": {
        "first_name": {"max_length": 30, "char_type": "latin"},
        "last_name": {"max_length": 50, "char_type": "latin"},
    },
    "profile": {
        "city": {
            "max_length": 32,
            "char_type": "latin",
            "dependent_fields": {
                "profile.gender": {
                    "Male": ["Bogota", "Medellin", "Cali"],
                    "Female": "Florida",
                },
                "profile.country": {
                    "CO": ["Bogota", "Medellin", "Cali"],
                    "US": "Florida"
                }
            }
        },
        "country": {"max_length": 2, "optional_values": ["US", "CA", "MX", "BR"]},
        "phone_number": {"max_length": 15, "format": "phone"},
        "mailing_address": {"max_length": 40},
    },
    "extra_info": {
        "arabic_name": {"max_length": 20, "char_type": "arabic"},
        "arabic_first_name": {"max_length": 20, "char_type": "arabic", "allow_empty": True},
        "arabic_last_name": {"max_length": 50, "char_type": "arabic"},
    },
"""
import functools
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
    return validate_user_fields(user, user, account_fields)


def validate_profile_fields(user, profile_fields):
    """
    Validates the profile fields of the user.

    Args:
        user (User): The user instance.
        profile_fields (dict): Dictionary of required fields and their validation rules.

    Returns:
        dict: A dictionary with invalid profile fields and their errors.
    """
    return validate_user_fields(user, getattr(user, "profile", None), profile_fields)


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

    return validate_user_fields(user, extra_info, extra_info_fields)


def validate_user_fields(user, instance, fields):
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
        errors += validate_dependent_field(user, value, rules.get("dependent_fields", {}))
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


def validate_dependent_field(user, value, arguments):
    """
    Validates a field based on dependencies with other fields in the user model.

    This function checks whether a field's value is valid based on the values of other related fields
    defined in the `dependent_fields` attribute. If the related field's value is not listed in the
    dependency mapping, the validation passes by default.

    Args:
        user (User): The user instance whose related fields will be checked.
        value (str): The value of the field being validated.
        arguments (dict): A dictionary defining the dependent fields and their valid value mappings.

    Returns:
        list: A list of validation error messages. Returns an empty list if valid.

    Example:
        Given the following dependency settings:

        ```python
        "city": {
            "dependent_fields": {
                "profile.gender": {
                    "Male": ["Google", "Microsoft", "Amazon"],
                    "Female": ["Facebook", "Apple", "Netflix"],
                },
                "profile.country": {
                    "CO": ["Bogota", "Medellin", "Cali"],
                    "US": "Florida"
                }
            }
        }
        ```

        - If `profile.gender` is "Male", valid values for `city` are "Google", "Microsoft", or "Amazon".
        - If `profile.gender` is "Female", valid values for `city` are "Facebook", "Apple", or "Netflix".
        - If `profile.country` is "CO", valid values for `city` are "Bogota", "Medellin", or "Cali".
        - If `profile.country` is "US", the only valid value for `city` is "Florida".

        If a mismatch is found, an error message is returned.
    """
    def get_attr(instance, attr):
        """
        Recursively retrieves an attribute from a nested object.

        Args:
            instance (object): The root object (e.g., user, user.profile, user.extrainfo).
            attr (str): The attribute path, supporting dot notation (e.g., "profile.country").

        Returns:
            str: The attribute value as a string. If the attribute does not exist, an empty string is returned.
        """
        def _getattr(obj, attr):
            return getattr(obj, attr, "")

        return str(functools.reduce(_getattr, [instance] + attr.split(".")))

    errors = []

    if not arguments or not isinstance(arguments, dict):
        return errors

    for argument_field, argument in arguments.items():
        argument_value = get_attr(user, argument_field)
        conditions = argument.get(argument_value)

        if not conditions:
            continue

        if isinstance(conditions, list) and value not in conditions:
            errors.append(f"{value} is not a valid option from {conditions}")
        elif isinstance(conditions, str) and value != conditions:
            errors.append(f"{value} is different from {conditions}")

    return errors
