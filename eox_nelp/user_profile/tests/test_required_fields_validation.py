"""This file contains all the tests for the validate_required_user_fields function.

Classes:
    ValidateRequiredUserFieldsTestCase: Class to test validate_required_user_fields function.
"""

from unittest.mock import patch

from custom_reg_form.models import ExtraInfo
from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from eox_nelp.user_profile import required_fields_validation
from eox_nelp.user_profile.required_fields_validation import (
    validate_account_fields,
    validate_arabic,
    validate_char_type,
    validate_cp1252,
    validate_email,
    validate_extra_info_fields,
    validate_field,
    validate_format,
    validate_latin,
    validate_max_length,
    validate_numeric,
    validate_optional_values,
    validate_phone,
    validate_profile_fields,
    validate_required_user_fields,
    validate_user_fields,
)

User = get_user_model()


class ValidateRequiredUserFieldsTestCase(TestCase):
    """Test case for validate_required_user_fields function."""

    @patch("eox_nelp.user_profile.required_fields_validation.validate_account_fields")
    @patch("eox_nelp.user_profile.required_fields_validation.validate_profile_fields")
    @patch("eox_nelp.user_profile.required_fields_validation.validate_extra_info_fields")
    def test_validate_required_user_fields(self, mock_validate_extrainfo, mock_validate_profile, mock_validate_account):
        """
        Test that the function correctly validates user fields.

        Expected behavior:
            - The function should call validate_account_fields with the correct arguments.
            - The function should call validate_profile_fields with the correct arguments.
            - The function should call validate_extra_info_fields with the correct arguments.
            - The function should return the expected dictionary structure.
        """
        user = User.objects.create(username="testuser")
        mock_validate_account.return_value = {"username": ["max_length exceeded"]}
        mock_validate_profile.return_value = {"first_name": ["invalid char_type"]}
        mock_validate_extrainfo.return_value = {}

        with override_settings(
            REQUIRED_USER_FIELDS={
                "account": {"username": {"max_length": 10}},
                "profile": {"first_name": {"char_type": "latin"}},
                "extra_info": {},
            }
        ):
            result = validate_required_user_fields(user)

        mock_validate_account.assert_called_once_with(user, {"username": {"max_length": 10}})
        mock_validate_profile.assert_called_once_with(user, {"first_name": {"char_type": "latin"}})
        mock_validate_extrainfo.assert_called_once_with(user, {})
        self.assertEqual(
            result,
            {
                "account": {"username": ["max_length exceeded"]},
                "profile": {"first_name": ["invalid char_type"]},
                "extra_info": {},
            }
        )


class ValidateAccountFieldsTestCase(TestCase):
    """Test case for validate_account_fields function."""

    @patch("eox_nelp.user_profile.required_fields_validation.validate_user_fields")
    def test_validate_account_fields(self, mock_validate_user_fields):
        """
        Test that the function correctly validates account fields.

        Expected behavior:
            - The function should call validate_user_fields with the correct arguments.
            - The function should return the result from validate_user_fields.
        """
        user = User.objects.create(username="testuser")
        mock_validate_user_fields.return_value = {"username": ["max_length exceeded"]}
        result = validate_account_fields(user, {"username": {"max_length": 10}})

        mock_validate_user_fields.assert_called_once_with(user, {"username": {"max_length": 10}})
        self.assertEqual(result, {"username": ["max_length exceeded"]})


class ValidateProfileFieldsTestCase(TestCase):
    """Test case for validate_profile_fields function."""

    @patch("eox_nelp.user_profile.required_fields_validation.validate_user_fields")
    def test_validate_profile_fields(self, mock_validate_user_fields):
        """
        Test that the function correctly validates profile fields.

        Expected behavior:
            - The function should call validate_user_fields with the correct arguments.
            - The function should return the result from validate_user_fields.
        """
        user = User.objects.create(username="testuser")
        user.profile = type("ProfileMock", (), {"first_name": "invalid_name"})()
        mock_validate_user_fields.return_value = {"first_name": ["invalid char_type"]}

        result = validate_profile_fields(user, {"first_name": {"char_type": "latin"}})

        mock_validate_user_fields.assert_called_once_with(user.profile, {"first_name": {"char_type": "latin"}})
        self.assertEqual(result, {"first_name": ["invalid char_type"]})


class ValidateExtraInfoFieldsTestCase(TestCase):
    """Test case for validate_extra_info_fields function."""

    @patch("eox_nelp.user_profile.required_fields_validation.validate_user_fields")
    def test_validate_extra_info_fields(self, mock_validate_user_fields):
        """
        Test that the function correctly validates extra_info fields.

        Expected behavior:
            - The function should call validate_user_fields with the correct arguments.
            - The function should return the result from validate_user_fields.
        """
        user = User.objects.create(username="testuser")
        user.extrainfo = ExtraInfo(arabic_first_name="invalid-arabic-name")
        mock_validate_user_fields.return_value = {"arabic_first_name": ["invalid char_type"]}

        result = validate_extra_info_fields(user, {"arabic_first_name": {"char_type": "arabic"}})

        mock_validate_user_fields.assert_called_once_with(
            user.extrainfo,
            {"arabic_first_name": {"char_type": "arabic"}},
        )
        self.assertEqual(result, {"arabic_first_name": ["invalid char_type"]})


class ValidateUserFieldsTestCase(TestCase):
    """Test case for validate_user_fields function."""

    @patch("eox_nelp.user_profile.required_fields_validation.validate_field")
    def test_validate_user_fields(self, mock_validate_field):
        """
        Test that the function correctly validates fields for a given user instance.

        Expected behavior:
            - The function should call validate_field for each field in fields.
            - The function should return a dictionary with invalid fields and their errors.
        """
        instance = type("UserMock", (), {"username": "testuser", "email": "invalid_email"})()
        fields = {
            "username": {"max_length": 10},
            "email": {"format": "email"},
        }
        mock_validate_field.side_effect = [[], ["invalid format"]]

        result = validate_user_fields(instance, fields)

        self.assertEqual(mock_validate_field.call_count, 2)
        self.assertEqual(result, {"username": [], "email": ["invalid format"]})

    def test_validate_user_fields_with_no_instance(self):
        """
        Test that the function returns an empty dictionary when the instance is None.

        Expected behavior:
            - The function should return an empty dictionary.
        """
        result = validate_user_fields(None, {"username": {"max_length": 10}})

        self.assertEqual(result, {})

    def test_validate_user_fields_with_empty_value(self):
        """
        Test that the function returns the right message when the attribute is empty.

        Expected behavior:
            - The function should return a dictionary with expected error.
        """
        instance = type("UserMock", (), {"username": ""})()

        result = validate_user_fields(instance, {"username": {"max_length": 10}})

        self.assertEqual(result, {"username": ["Empty field"]})

    def test_validate_user_fields_with_invalid_field(self):
        """
        Test that the function returns an empty dictionary when an invlaid field has been set.

        Expected behavior:
            - A warning is logged with the right message.
            - The function should return an empty dictionary.
        """
        instance = type("UserMock", (), {"username": ""})()

        with self.assertLogs(required_fields_validation.__name__, level="WARNING") as logs:
            result = validate_user_fields(instance, {"invalid": {"max_length": 10}})

        self.assertEqual(logs.output, [
            f"WARNING:{required_fields_validation.__name__}:Invalid configuration for invalid field",
        ])
        self.assertEqual(result, {})


class ValidateFieldTestCase(TestCase):
    """Test case for validate_field function."""

    @patch("eox_nelp.user_profile.required_fields_validation.validate_max_length")
    @patch("eox_nelp.user_profile.required_fields_validation.validate_char_type")
    @patch("eox_nelp.user_profile.required_fields_validation.validate_format")
    @patch("eox_nelp.user_profile.required_fields_validation.validate_optional_values")
    def test_validate_field_calls_validators(
        self,
        mock_validate_optional_values,
        mock_validate_format,
        mock_validate_char_type,
        mock_validate_max_length,
    ):
        """
        Test that the function calls the corresponding validator for each rule.

        Expected behavior:
            - The function should call validate_max_length with the correct arguments.
            - The function should call validate_char_type with the correct arguments.
            - The function should call validate_format with the correct arguments.
            - The function should call validate_optional_values with the correct arguments.
        """
        value = "testvalue"
        rules = {
            "max_length": 10,
            "char_type": "latin",
            "format": "email",
            "optional_values": ["test", "value"],
        }

        validate_field(value, rules)

        mock_validate_max_length.assert_called_once_with(value, 10)
        mock_validate_char_type.assert_called_once_with(value, "latin")
        mock_validate_format.assert_called_once_with(value, "email")
        mock_validate_optional_values.assert_called_once_with(value, ["test", "value"])

    @patch("eox_nelp.user_profile.required_fields_validation.validate_max_length", return_value=True)
    @patch("eox_nelp.user_profile.required_fields_validation.validate_char_type", return_value=True)
    @patch("eox_nelp.user_profile.required_fields_validation.validate_format", return_value=True)
    @patch("eox_nelp.user_profile.required_fields_validation.validate_optional_values", return_value=True)
    def test_validate_field_returns_empty_list_if_valid(self, *_):
        """
        Test that the function returns an empty list if the field is valid.

        Expected behavior:
            - The function should return an empty list when all validations pass.
        """
        value = "validvalue"
        rules = {
            "max_length": 10,
            "char_type": "latin",
            "format": "email",
            "optional_values": ["validvalue"],
        }

        result = validate_field(value, rules)

        self.assertEqual(result, [])

    @patch("eox_nelp.user_profile.required_fields_validation.validate_max_length", return_value=False)
    @patch("eox_nelp.user_profile.required_fields_validation.validate_char_type", return_value=True)
    @patch("eox_nelp.user_profile.required_fields_validation.validate_format", return_value=False)
    @patch("eox_nelp.user_profile.required_fields_validation.validate_optional_values", return_value=True)
    def test_validate_field_returns_errors_if_invalid(self, *_):
        """
        Test that the function returns a list of error messages if the field is invalid.

        Expected behavior:
            - The function should return a list containing error messages for each failed validation.
        """
        value = "invalidvalue"
        rules = {
            "max_length": 10,
            "char_type": "latin",
            "format": "email",
            "optional_values": ["validvalue"],
        }

        result = validate_field(value, rules)

        self.assertEqual(result, ["max_length with argument 10 failed", "format with argument email failed"])


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
        with patch(f"eox_nelp.user_profile.required_fields_validation.validate_{value}") as mock_validator:
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
        with patch(f"eox_nelp.user_profile.required_fields_validation.validate_{field_format}") as mock_validator:
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

    @patch("eox_nelp.user_profile.required_fields_validation.PhoneNumber.from_string")
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

    @patch("eox_nelp.user_profile.required_fields_validation.PhoneNumber.from_string")
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
