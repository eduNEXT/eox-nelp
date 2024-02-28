"""This file contains all the test for the Nelp registration form factory.
Classes:
    RegistrationFormFactoryTestCase: Test NelpRegistrationFormFactory login and class manipulation.
"""
from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from mock import Mock

from eox_nelp.edxapp_wrapper.site_configuration import configuration_helpers
from eox_nelp.edxapp_wrapper.user_api import accounts
from eox_nelp.user_authn.views.registration_form import NelpRegistrationFormFactory


def mock_responses(responses):
    """Function that manage the response of a mock based in its args.
    You configre using a dict defining in the dict they key of each the args is used the response
    of the function would be.
    eg:
    my_mock.foo.side_effect = mock_responses({
        'x': 43,
        'y': [4,5,6]
    })
    my_mock.foo('x') # => 43
    my_mock.foo('y') # => [4,5,6]
    my_mock.foo('diferent_arg') # => None
    """
    return lambda input, default_value=None: responses[input] if input in responses else default_value


class RegistrationFormFactoryTestCase(TestCase):
    """Test for Nelp registration form factory"""
    EXTRA_FIELDS = [
        "confirm_email",
        "first_name",
        "last_name",
        "city",
        "state",
        "country",
    ]

    def setUp(self):
        """
        Create site since the view use the request.site attribute to determine the current domain.
        """
        self.request = Mock()
        self.field_order = [
            "email",
            "name",
            "username",
            "password",
            "confirm_email",
            "first_name",
            "last_name",
            "city",
            "state",
            "country",
        ]

    def tearDown(self):
        """Reset mocks"""
        configuration_helpers.reset_mock()
        self.request.reset_mock()

    def test_custom_fields(self):
        """Test the integration of custom fields for registration form.
        Expected behaviour:
            - field_order list attr of the form factory has extended_profile fields.
            - for each extended_profile_field:
              - NelpRegistrationFormFactory class has the _add{field} attr
              - account class has the desired attr `...SELECT_MSG for field.
              - account class has the desired value of `...SELECT_MSG attr.
              - account class has the desired attr `...TXT_MSG for field.
              - account class has the desired value of `...TXT_MSG attr.
              - field_handlers dict has the key of the each_field_name.

        """
        extended_profile_fields = ["hobby", "sport", "movie"]
        self.request.LANGUAGE_CODE = "en"
        configuration_helpers.get_value.side_effect = mock_responses(
            {"extended_profile_fields": extended_profile_fields}
        )
        nelp_form_factory = NelpRegistrationFormFactory()
        nelp_form_factory.field_order = self.field_order
        nelp_form_factory.EXTRA_FIELDS = self.EXTRA_FIELDS
        nelp_form_factory.field_handlers = {}

        nelp_form_factory.get_registration_form(self.request)

        self.assertListEqual(nelp_form_factory.field_order, self.field_order + sorted(extended_profile_fields))
        for field_name in extended_profile_fields:
            self.assertTrue(hasattr(NelpRegistrationFormFactory, f"_add_{field_name}_field"))
            self.assertTrue(hasattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_SELECT_MSG"))
            self.assertEqual(
                getattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_SELECT_MSG"), f"{_('Select your')} {field_name}"
            )
            self.assertTrue(hasattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_TEXT_MSG"))
            self.assertEqual(
                getattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_TEXT_MSG"), f"{_('Enter your')} {field_name}"
            )
            self.assertTrue(field_name in nelp_form_factory.field_handlers)

    def test_custom_fields_with_translations(self):
        """Test the integration of custom fields for registration form with translation configured.
        Expected behaviour:
            - field_order list attr of the form factory has extended_profile fields.
            - for each extended_profile_field:
              - NelpRegistrationFormFactory class has the _add{field} attr
              - account class has the desired attr `...SELECT_MSG for field.
              - account class has the desired value translated of `...SELECT_MSG attr.
              - account class has the desired attr `...TXT_MSG for field.
              - account class has the desired value translated of `...TXT_MSG attr.
              - field_handlers dict has the key of the each_field_name.

        """
        extended_profile_fields_translations = {
            "ar": {
                "hobby": "هواية",
                "sport": "رياضة",
                "movie": "فيلم",
            }
        }
        extended_profile_fields = ["hobby", "sport", "movie"]
        self.request.LANGUAGE_CODE = "ar"
        configuration_helpers.get_value.side_effect = mock_responses(
            {
                "extended_profile_fields": extended_profile_fields,
                "extended_profile_fields_translations": extended_profile_fields_translations,
            }
        )
        nelp_form_factory = NelpRegistrationFormFactory()
        nelp_form_factory.field_order = self.field_order
        nelp_form_factory.EXTRA_FIELDS = self.EXTRA_FIELDS
        nelp_form_factory.field_handlers = {}
        nelp_form_factory.get_registration_form(self.request)

        self.assertListEqual(nelp_form_factory.field_order, self.field_order + sorted(extended_profile_fields))
        for field_name in extended_profile_fields:
            self.assertTrue(hasattr(NelpRegistrationFormFactory, f"_add_{field_name}_field"))
            self.assertTrue(hasattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_SELECT_MSG"))
            self.assertEqual(
                getattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_SELECT_MSG"),
                f"{_('Select your')} {extended_profile_fields_translations[self.request.LANGUAGE_CODE][field_name]}",
            )
            self.assertTrue(hasattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_TEXT_MSG"))
            self.assertEqual(
                getattr(accounts, f"REQUIRED_FIELD_{field_name.upper()}_TEXT_MSG"),
                f"{_('Enter your')} {extended_profile_fields_translations[self.request.LANGUAGE_CODE][field_name]}",
            )
            self.assertTrue(field_name in nelp_form_factory.field_handlers)

    def test_not_extended_profile_fields(self):
        """Test the integration of custom fields without definition or configuration..
        Expected behaviour:
            - field_order list attr of the form factory was not modifield.
            - field_handlers dict was not modified.
        """
        self.request.LANGUAGE_CODE = "en"
        configuration_helpers.get_value.side_effect = mock_responses({})
        nelp_form_factory = NelpRegistrationFormFactory()
        nelp_form_factory.field_order = self.field_order
        nelp_form_factory.EXTRA_FIELDS = self.EXTRA_FIELDS
        nelp_form_factory.field_handlers = {}
        nelp_form_factory.get_registration_form(self.request)

        self.assertListEqual(nelp_form_factory.field_order, self.field_order)
        self.assertDictEqual(nelp_form_factory.field_handlers, {})
