"""This file contains all the test for the one_time_password API V1 views.py file.

Classes:
    GenerateOTPTestCase: Class to test GenerateOTP view
"""

from ddt import data, ddt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from eox_nelp.one_time_password.api.v1 import views
from eox_nelp.tests.mixins import POSTAuthenticatedTestMixin
from eox_nelp.tests.utils import get_cache_expiration_time

User = get_user_model()


@ddt
class GenerateOTPTestCase(POSTAuthenticatedTestMixin, APITestCase):
    """Test case for generate OTP view."""
    reverse_viewname = "one-time-password-api:v1:generate-otp"

    @data({}, {"not_phone_number": 3123123123})
    def test_generate_otp_without_right_payload(self, wrong_payload):
        """
        Test  the post request to generate otp is not running due missing keys in the payload sent.
        Expected behavior:
            - Check the response say is missing some keys.
            - Status code 400.
        """
        url_endpoint = reverse(self.reverse_viewname)

        response = self.client.post(url_endpoint, wrong_payload, format="json")

        self.assertDictEqual(response.json(), {"detail": "missing phone_number in data."})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_otp(self):
        """
        Test  the post request to generate otp.
        Expected behavior:
            - Check logging generation msg
            - Check the response say success otp generated.
            - Status code 201.
            - Check that in cache the OTP is stored(not None).
            - Check that the expiration OTP is less than default value 600s, and bigger than a prudent execution time.
            - Check the length of the OTP code is the default 8.
        """
        payload = {"phone_number": 3218995688}
        url_endpoint = reverse(self.reverse_viewname)
        user_otp_key = f"{self.user.username}-{payload['phone_number']}"

        with self.assertLogs(views.__name__, level="INFO") as logs:
            response = self.client.post(url_endpoint, payload, format="json")

        otp_stored = cache.get(user_otp_key)
        expiration_otp = get_cache_expiration_time(user_otp_key)
        self.assertEqual(logs.output, [
            f"INFO:{views.__name__}:generating otp {user_otp_key[:-5]}*****"
        ])
        self.assertDictEqual(response.json(), {"message": "Success generate-otp!"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(otp_stored)
        self.assertTrue(500 < expiration_otp < 600)
        self.assertEqual(len(otp_stored), 8)

    @override_settings(
        PHONE_VALIDATION_OTP_LENGTH=20,
        PHONE_VALIDATION_OTP_CHARSET="01",
        PHONE_VALIDATION_OTP_TIMEOUT=1200,
    )
    def test_generate_otp_custom_settings(self):
        """
        Test  the post request to generate otp with custom settings.
        Expected behavior:
            - Check logging generation msg
            - Check the response say success otp generated..
            - Status code 201.
            - Check that in cache the OTP is stored(not None).
            - Check that the expiration OTP is less than settings value, and bigger than a prudent execution time.
            - Check the length of the OTP code is the settings value.
            - Check that the chars of setting value is presented in the otp code.
        """
        payload = {"phone_number": 3218995688}
        url_endpoint = reverse(self.reverse_viewname)
        user_otp_key = f"{self.user.username}-{payload['phone_number']}"

        with self.assertLogs(views.__name__, level="INFO") as logs:
            response = self.client.post(url_endpoint, payload, format="json")

        otp_stored = cache.get(user_otp_key)
        expiration_otp = get_cache_expiration_time(user_otp_key)
        self.assertEqual(logs.output, [
            f"INFO:{views.__name__}:generating otp {user_otp_key[:-5]}*****"
        ])
        self.assertDictEqual(response.json(), {"message": "Success generate-otp!"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(otp_stored)
        self.assertTrue(
            (settings.PHONE_VALIDATION_OTP_TIMEOUT - 100) < expiration_otp < settings.PHONE_VALIDATION_OTP_TIMEOUT
        )
        self.assertEqual(len(otp_stored), settings.PHONE_VALIDATION_OTP_LENGTH)
        self.assertIn(settings.PHONE_VALIDATION_OTP_CHARSET[0], otp_stored)
