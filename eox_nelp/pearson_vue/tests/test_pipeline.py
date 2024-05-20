"""
This module contains unit tests for the functions in pipeline.py.
"""
import unittest
from unittest.mock import MagicMock

from ddt import data, ddt
from django.contrib.auth import get_user_model
from django_countries.fields import Country

from eox_nelp.edxapp_wrapper.student import anonymous_id_for_user
from eox_nelp.pearson_vue.pipeline import get_user_data

User = get_user_model()


@ddt
class TestGetUserData(unittest.TestCase):
    """
    Unit tests for the get_user_data function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user, _ = User.objects.get_or_create(
            username="Gamekeeper2024",
            first_name="Rubeus",
            last_name="Hagrid",
            email="rubeus.hagrid@hogwarts.com"

        )
        self.profile = MagicMock(
            phone_number="+443214567895",
            mailing_address="Abbey Road 25",
            city="London",
            country=Country("GB")

        )
        anonymous_id_for_user.return_value = "ABCDF1245678899"
        setattr(User, "profile", self.profile)

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        anonymous_id_for_user.reset_mock()

    @data("+443214567895", "3214567895")
    def test_get_user_data(self, phone):
        """
        Test get_user_data , this checks that the response is the expected when the
        phone_number has and doesn't have the country code.

            Expected behavior:
            - The result is as the expected output.
        """
        phone_number = phone[3:] if phone.startswith("+") else phone
        country_code = "44"  # This is the code for GB
        self.profile.phone_number = phone

        expected_output = {
            "anonymous_user_id": anonymous_id_for_user(self.user, None),
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "address": self.profile.mailing_address,
            "city": self.profile.city,
            "country": self.profile.country.code,
            "phone_number": phone_number,
            "phone_country_code": country_code,
            "mobile_number": phone_number,
            "mobile_country_code": country_code,
        }

        result = get_user_data(self.user.id)

        self.assertEqual(result, expected_output)
