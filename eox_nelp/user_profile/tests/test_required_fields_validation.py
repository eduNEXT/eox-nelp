"""
This file contains unit tests for the user field validation functions in the required_fields_validation module.

The tests ensure that:
- The validation functions correctly apply the rules defined in the REQUIRED_USER_FIELDS setting.
- The correct validators are called for each field type.
- The functions return the expected validation errors for incorrect field values.
- Logging warnings are properly generated for invalid configurations.

Test Classes:
    - ValidateRequiredUserFieldsTestCase: Tests validate_required_user_fields function.
    - ValidateAccountFieldsTestCase: Tests validate_account_fields function.
    - ValidateProfileFieldsTestCase: Tests validate_profile_fields function.
    - ValidateExtraInfoFieldsTestCase: Tests validate_extra_info_fields function.
    - ValidateUserFieldsTestCase: Tests validate_user_fields function.
    - ValidateFieldTestCase: Tests validate_field function.
    - ValidateDependentFieldTestCase : Tests validate_dependent_field function.
"""
from unittest.mock import patch

from custom_reg_form.models import ExtraInfo
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from eox_nelp.user_profile import required_fields_validation
from eox_nelp.user_profile.required_fields_validation import (
    validate_account_fields,
    validate_dependent_field,
    validate_extra_info_fields,
    validate_field,
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

        mock_validate_user_fields.assert_called_once_with(user, user, {"username": {"max_length": 10}})
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

        mock_validate_user_fields.assert_called_once_with(user, user.profile, {"first_name": {"char_type": "latin"}})
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
        ExtraInfo.objects.create(user=user, arabic_first_name="invalid-arabic-name")  # pylint: disable=no-member
        mock_validate_user_fields.return_value = {"arabic_first_name": ["invalid char_type"]}

        result = validate_extra_info_fields(user, {"arabic_first_name": {"char_type": "arabic"}})

        mock_validate_user_fields.assert_called_once_with(
            user,
            user.extrainfo,
            {"arabic_first_name": {"char_type": "arabic"}},
        )
        self.assertEqual(result, {"arabic_first_name": ["invalid char_type"]})

    @patch("eox_nelp.user_profile.required_fields_validation.validate_user_fields")
    def test_validate_without_extrainfo(self, mock_validate_user_fields):
        """
        Test that the function return all the model fields as empty when the user doesn't have
        the extrainfo attribute.

        Expected behavior:
            - The function shouldn't call validate_user_fields.
            - The function should return all required fields with empty field message.
        """
        user = User.objects.create(username="testuser")
        expected_result = {
            "arabic_name": ["Empty field"],
            "arabic_first_name": ["Empty field"],
            "arabic_last_name": ["Empty field"],
            "national_id": ["Empty field"],
        }

        result = validate_extra_info_fields(
            user,
            {
                "arabic_name": {"max_length": 20, "char_type": "arabic"},
                "arabic_first_name": {"max_length": 20, "char_type": "arabic"},
                "arabic_last_name": {"max_length": 50, "char_type": "arabic"},
                "national_id": {"max_length": 50, "char_type": "latin", "format": "numeric"},
            },
        )

        mock_validate_user_fields.assert_not_called()
        self.assertEqual(result, expected_result)


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
        user = User.objects.create(username="testuser")
        instance = type("UserMock", (), {"username": "testuser", "email": "invalid_email"})()
        fields = {
            "username": {"max_length": 10},
            "email": {"format": "email"},
        }
        mock_validate_field.side_effect = [[], ["invalid format"]]

        result = validate_user_fields(user, instance, fields)

        self.assertEqual(mock_validate_field.call_count, 2)
        self.assertEqual(result, {"username": [], "email": ["invalid format"]})

    def test_validate_user_fields_with_no_instance(self):
        """
        Test that the function returns an empty dictionary when the instance is None.

        Expected behavior:
            - The function should return an empty dictionary.
        """
        user = User.objects.create(username="testuser")

        result = validate_user_fields(user, None, {"username": {"max_length": 10}})

        self.assertEqual(result, {})

    def test_validate_user_fields_with_invalid_field(self):
        """
        Test that the function returns an empty dictionary when an invlaid field has been set.

        Expected behavior:
            - A warning is logged with the right message.
            - The function should return an empty dictionary.
        """
        user = User.objects.create(username="testuser")
        instance = type("UserMock", (), {"username": ""})()

        with self.assertLogs(required_fields_validation.__name__, level="WARNING") as logs:
            result = validate_user_fields(user, instance, {"invalid": {"max_length": 10}})

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

    def test_validate_field_with_empty_value(self):
        """
        Test that the function returns the right message when the attribute is empty.

        Expected behavior:
            - The function should return the expected error.
        """
        result = validate_field("", {"max_length": 10, "allow_empty": False})

        self.assertEqual(result, ["Empty field"])

    def test_validate_field_with_allow_empty(self):
        """
        Test that the function returns the expected validation error when the value is None and the allow_empty is True.

        Expected behavior:
            - The function should return the expected error.
        """
        result = validate_field(None, {"max_length": 10, "allow_empty": True, "format": "email"})

        self.assertEqual(result, ["format with argument email failed"])


class ValidateDependentFieldTestCase(TestCase):
    """Test case for validate_dependent_field function."""

    def test_validate_dependent_field_valid_values(self):
        """
        Test that the function returns an empty list if the dependent field has a valid value.

        Expected behavior:
            - The function should return an empty list when the value matches the expected conditions.
        """
        user_mock = type("UserMock", (), {"gender": "Male"})()
        value = "Google"
        rules = {"gender": {"Male": ["Google", "Microsoft"]}}

        result = validate_dependent_field(user_mock, value, rules)

        self.assertEqual(result, [])

    def test_validate_dependent_field_invalid_value_list(self):
        """
        Test that the function returns an error if the value is not in the allowed list.

        Expected behavior:
            - The function should return an error message indicating the invalid value.
        """
        user_mock = type("UserMock", (), {"gender": "Male"})()
        value = "Facebook"
        rules = {"gender": {"Male": ["Google", "Microsoft"]}}

        result = validate_dependent_field(user_mock, value, rules)

        self.assertEqual(result, ["Facebook is not a valid option from ['Google', 'Microsoft']"])

    def test_validate_dependent_field_invalid_value_str(self):
        """
        Test that the function returns an error if the value does not match the expected string.

        Expected behavior:
            - The function should return an error message indicating the mismatch.
        """
        user_mock = type("UserMock", (), {"gender": "Other"})()
        value = "Freelancer"
        rules = {"gender": {"Other": "Self-Employed"}}

        result = validate_dependent_field(user_mock, value, rules)

        self.assertEqual(result, ["Freelancer is different from Self-Employed"])

    def test_validate_dependent_field_nested_attribute(self):
        """
        Test that the function correctly retrieves nested attributes.

        Expected behavior:
            - The function should correctly access nested attributes and validate the value accordingly.
        """
        profile_mock = type("ProfileMock", (), {"country": "CO"})()
        user_mock = type("UserMock", (), {"profile": profile_mock})()
        value = "Bogota"
        rules = {"profile.country": {"CO": ["Bogota", "Medellin"]}}

        result = validate_dependent_field(user_mock, value, rules)

        self.assertEqual(result, [])

    def test_validate_dependent_field_no_matching_condition(self):
        """
        Test that the function returns an empty list if there is no matching condition.

        Expected behavior:
            - The function should return an empty list when no rule applies.
        """
        user_mock = type("UserMock", (), {"gender": "Female"})()
        value = "Google"
        rules = {"gender": {"Male": ["Google", "Microsoft"]}}

        result = validate_dependent_field(user_mock, value, rules)

        self.assertEqual(result, [])
