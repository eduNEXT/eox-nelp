"""
This file contains unit tests for the validation functions in the eox_nelp.validators module.

The tests ensure that:
- Each validation function correctly enforces its constraints (e.g., max_length, char_type, format).
- The correct validator functions are called dynamically where applicable.
- The functions return expected results for valid and invalid inputs.

Test Classes:
    - ValidateMaxLengthTestCase: Tests validate_max_length function.
    - ValidateOptionalValuesTestCase: Tests validate_optional_values function.
    - ValidateCharTypeTestCase: Tests validate_char_type function.
    - ValidateLatinTestCase: Tests validate_latin function.
    - ValidateArabicTestCase: Tests validate_arabic function.
    - ValidateCp1252TestCase: Tests validate_cp1252 function.
    - ValidateFormatTestCase: Tests validate_format function.
    - ValidateEmailTestCase: Tests validate_email function.
    - ValidatePhoneTestCase: Tests validate_phone function.
    - ValidateNumericTestCase: Tests validate_numeric function.
"""
from unittest.mock import patch

from ddt import data, ddt
from django.test import TestCase

from eox_nelp.validators import (
    validate_arabic,
    validate_char_type,
    validate_cp1252,
    validate_email,
    validate_format,
    validate_latin,
    validate_max_length,
    validate_numeric,
    validate_optional_values,
    validate_phone,
)


class ValidateMaxLengthTestCase(TestCase):
    """Test case for validate_max_length function."""

    def test_validate_max_length_valid(self):
        """
        Test that the function returns True when the value length is within the limit.

        Expected behavior:
            - The function should return True if the length of the value is less than or equal to max_length.
        """
        result = validate_max_length("short", 10)
        self.assertTrue(result)

    def test_validate_max_length_invalid(self):
        """
        Test that the function returns False when the value length exceeds the limit.

        Expected behavior:
            - The function should return False if the length of the value exceeds max_length.
        """
        result = validate_max_length("this is too long", 5)
        self.assertFalse(result)


class ValidateOptionalValuesTestCase(TestCase):
    """Test case for validate_optional_values function."""

    def test_validate_optional_values_valid(self):
        """
        Test that the function returns True when the value is in the allowed list.

        Expected behavior:
            - The function should return True if the value exists in allowed_values.
        """
        result = validate_optional_values("US", ["US", "CA", "MX"])
        self.assertTrue(result)

    def test_validate_optional_values_invalid(self):
        """
        Test that the function returns False when the value is not in the allowed list.

        Expected behavior:
            - The function should return False if the value does not exist in allowed_values.
        """
        result = validate_optional_values("FR", ["US", "CA", "MX"])
        self.assertFalse(result)


@ddt
class ValidateCharTypeTestCase(TestCase):
    """Test case for validate_char_type function."""

    @data("latin", "arabic", "cp1252")
    def test_validate_char_type_calls_correct_validator(self, value):
        """
        Test that the function calls the correct validator based on char_type.

        Expected behavior:
            - The function should call the corresponding validator dynamically.
        """
        with patch(f"eox_nelp.validators.validate_{value}") as mock_validator:
            validate_char_type("test", value)

            mock_validator.assert_called_once_with("test")

    def test_validate_char_type_returns_false_for_invalid_type(self):
        """
        Test that the function returns False when an unknown char_type is given.

        Expected behavior:
            - The function should return False if char_type is not in the predefined options.
        """
        result = validate_char_type("test", "unknown_type")
        self.assertFalse(result)


@ddt
class ValidateLatinTestCase(TestCase):
    """Test case for validate_latin function."""

    @data("Hello", "Café", "Jean-Pierre", "Smith Jr.", "L'étoile")
    def test_validate_latin_valid(self, value):
        """
        Test that the function returns True for valid Latin characters.

        Expected behavior:
            - The function should return True if the value contains only Latin characters and standard punctuation.
        """
        self.assertTrue(validate_latin(value))

    @data("مرحبا", "你好", "こんにちは", "123$", "@#€")
    def test_validate_latin_invalid(self, value):
        """
        Test that the function returns False for non-Latin characters.

        Expected behavior:
            - The function should return False if the value contains non-Latin characters.
        """
        self.assertFalse(validate_latin(value))


@ddt
class ValidateArabicTestCase(TestCase):
    """Test case for validate_arabic function."""

    @data("مرحبا", "السلام عليكم", "أهلاً وسهلاً")
    def test_validate_arabic_valid(self, value):
        """
        Test that the function returns True for valid Arabic script characters.

        Expected behavior:
            - The function should return True if the value contains only Arabic script characters.
        """
        self.assertTrue(validate_arabic(value))

    @data("Hello", "123", "Café", "!@#", "こんにちは")
    def test_validate_arabic_invalid(self, value):
        """
        Test that the function returns False for non-Arabic characters.

        Expected behavior:
            - The function should return False if the value contains non-Arabic characters.
        """
        self.assertFalse(validate_arabic(value))


@ddt
class ValidateCp1252TestCase(TestCase):
    """Test case for validate_cp1252 function."""

    @data("Hello", "Café", "ÆØÅ", "¡Hola!")
    def test_validate_cp1252_valid(self, value):
        """
        Test that the function returns True for valid CP1252 characters.

        Expected behavior:
            - The function should return True if the value contains only CP1252-compatible characters.
        """
        self.assertTrue(validate_cp1252(value))

    @data("你好", "こんにちは", "مرحبا", "∑", "≠")
    def test_validate_cp1252_invalid(self, value):
        """
        Test that the function returns False for non-CP1252 characters.

        Expected behavior:
            - The function should return False if the value contains non-CP1252 characters.
        """
        self.assertFalse(validate_cp1252(value))


@ddt
class ValidateFormatTestCase(TestCase):
    """Test case for validate_format function."""

    @data("email", "phone", "numeric")
    def test_validate_format_calls_correct_validator(self, field_format):
        """
        Test that the function calls the correct validator based on field_format.

        Expected behavior:
            - The function should call the corresponding validator dynamically.
        """
        value = "test_value"
        with patch(f"eox_nelp.validators.validate_{field_format}") as mock_validator:
            validate_format(value, field_format)

            # Assert: The correct validator should have been called.
            mock_validator.assert_called_once_with(value)

    def test_validate_format_returns_false_for_invalid_format(self):
        """
        Test that the function returns False when an unknown field_format is given.

        Expected behavior:
            - The function should return False if field_format is not in the predefined options.
        """
        result = validate_format("test_value", "unknown_format")
        self.assertFalse(result)


@ddt
class ValidateEmailTestCase(TestCase):
    """Test case for validate_email function."""

    @data("test@example.com", "user.name@domain.co.uk", "valid_email123@mail.com")
    def test_validate_email_valid(self, value):
        """
        Test that the function returns True for valid email addresses.

        Expected behavior:
            - The function should return True if the value is a valid email address.
        """
        self.assertTrue(validate_email(value))

    @data("invalid_email", "missing_at_symbol.com", "user@domain", "user@.com", "@domain.com")
    def test_validate_email_invalid(self, value):
        """
        Test that the function returns False for invalid email addresses.

        Expected behavior:
            - The function should return False if the value is not a valid email address.
        """
        self.assertFalse(validate_email(value))


@ddt
class ValidatePhoneTestCase(TestCase):
    """Test case for validate_phone function."""

    @patch("eox_nelp.validators.PhoneNumber.from_string")
    @data("+1234567890", "+49 170 1234567", "+1 (555) 123-4567")
    def test_validate_phone_valid(self, value, mock_phone):
        """
        Test that the function returns True for valid phone numbers.

        Expected behavior:
            - The function should return True if the value is a valid phone number.
        """
        mock_phone.return_value.is_valid.return_value = True

        result = validate_phone(value)

        self.assertTrue(result)

    @patch("eox_nelp.validators.PhoneNumber.from_string")
    @data("123456", "invalid_phone", "+1-abc-123456", "")
    def test_validate_phone_invalid(self, value, mock_phone):
        """
        Test that the function returns False for invalid phone numbers.

        Expected behavior:
            - The function should return False if the value is not a valid phone number.
        """
        mock_phone.return_value.is_valid.return_value = False

        result = validate_phone(value)

        self.assertFalse(result)


@ddt
class ValidateNumericTestCase(TestCase):
    """Test case for validate_numeric function."""

    @data("123456", "000000", "987654321")
    def test_validate_numeric_valid(self, value):
        """
        Test that the function returns True for numeric values.

        Expected behavior:
            - The function should return True if the value contains only numeric digits.
        """
        self.assertTrue(validate_numeric(value))

    @data("123abc", "12.34", "phone123", "one1two2three3")
    def test_validate_numeric_invalid(self, value):
        """
        Test that the function returns False for non-numeric values.

        Expected behavior:
            - The function should return False if the value contains non-numeric characters.
        """
        self.assertFalse(validate_numeric(value))
