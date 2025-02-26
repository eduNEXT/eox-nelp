"""
This module provides validation functions for user input fields.

The validators enforce constraints such as:
- Maximum length (`max_length`)
- Allowed values (`optional_values`)
- Character type restrictions (`char_type`)
- Format validation (`format`)

Validation Functions:
    - validate_max_length(value, max_length): Checks if the value does not exceed max_length.
    - validate_optional_values(value, allowed_values): Ensures the value is within a predefined list.
    - validate_char_type(value, char_type): Validates if the value matches a specific character type.
    - validate_latin(value): Validates that the value contains only Latin characters.
    - validate_arabic(value): Validates that the value contains only Arabic script characters.
    - validate_cp1252(value): Validates that the value contains only CP1252-compatible characters.
    - validate_format(value, field_format): Ensures the value follows a specific format (email, phone, numeric).
    - validate_email(value): Checks if the value is a valid email address.
    - validate_phone(value): Checks if the value is a valid phone number using django-phonenumber-field.
    - validate_numeric(value): Ensures the value contains only numeric digits.
"""
import re

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException


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
    try:
        phone = PhoneNumber.from_string(value)
    except NumberParseException:
        return False

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
