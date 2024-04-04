"""This file contains all the test for the phone_validation views.py file.
Classes:
    OTPMixin: Mixin for OTP views.
    GenerateOTPTestCase: Class to test GenerateOTP view
    ValidateOTPTestCase: Class to test ValidateOTP view
"""

from ddt import data, ddt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from mock import Mock
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from eox_nelp.phone_validation.api.v1 import views
from eox_nelp.tests.utils import get_cache_expiration_time

User = get_user_model()

NOT_ALLOWED_HTTP_METHODS = ["get", "delete", "patch", "put", "head"]


@ddt
class OTPMixin:
    """Mixin fot base OTP common code"""

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across OTP test cases.
        """
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(username="vader")
        setattr(self.user, "profile", Mock())
        self.client.force_authenticate(self.user)

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset some mock variables"""
        self.user.profile.reset_mock()

    @data(*NOT_ALLOWED_HTTP_METHODS)
    def test_method_not_allowed(self, method_name):
        """
        Test that an http verb or Method not configured are not ALLOWED.
        Expected behavior:.
            - Status code 405 METHOD_NOT_ALLOWED.
        """
        url_endpoint = reverse(self.reverse_viewname)
        method_caller = getattr(self.client, method_name)

        response = method_caller(url_endpoint, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_not_authenticated_user(self):
        """
        Test disallow by credentials the request to the list endpoint
        for the desired view.
        Expected behavior:
            - Return credentials of session were not provided.
            - Status code 403.
        """
        self.client.force_authenticate(user=None)
        url_endpoint = reverse(self.reverse_viewname)

        response = self.client.post(url_endpoint)

        self.assertContains(
            response,
            "Authentication credentials were not provided",
            status_code=status.HTTP_403_FORBIDDEN,
        )


@ddt
class GenerateOTPTestCase(OTPMixin, APITestCase):
    """Test case for generate OTP view."""
    reverse_viewname = "phone-validation-api:v1:generate-otp"

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


@ddt
class ValidateOTPTestCase(OTPMixin, APITestCase):
    """Test case for validate OTP view."""
    reverse_viewname = "phone-validation-api:v1:validate-otp"

    @data({}, {"not_phone_number": 3123123123}, {"not_one_time_password": 12345678, "phone_number": 3123123123})
    def test_validate_otp_without_right_payload(self, wrong_payload):
        """
        Test  the post request to validate otp is not running due missing keys in the payload sent.
        Expected behavior:
            - Check the response say is missing some keys.
            - Status code 400.
            - Check that user profile mock is not assigned and still is Mock.
            - Check that profile mock save method has not been called.
        """
        url_endpoint = reverse(self.reverse_viewname)

        response = self.client.post(url_endpoint, wrong_payload, format="json")

        self.assertDictEqual(response.json(), {"detail": "missing phone_number or one_time_password in data."})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(getattr(self.user.profile, "phone_number"), Mock)
        self.user.profile.save.assert_not_called()

    def test_validate_otp_without_right_validation_code(self):
        """
        Test  the post request to validate otp with wrong validation code.
        Expected behavior:
            - Check logging validation msg
            - Status code 403.
            - Check that user profile mock is not assigned and still is Mock.
            - Check that profile mock save method has not been called.
        """
        correct_otp = "correct17"
        payload = {"phone_number": 3219990000, "one_time_password": "password"}
        url_endpoint = reverse(self.reverse_viewname)
        user_otp_key = f"{self.user.username}-{payload['phone_number']}"
        cache.set(user_otp_key, correct_otp, timeout=600)

        with self.assertLogs(views.__name__, level="INFO") as logs:
            response = self.client.post(url_endpoint, payload, format="json")

        self.assertEqual(logs.output, [
            f"INFO:{views.__name__}:validating otp for {user_otp_key[:-5]}*****"
        ])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsInstance(getattr(self.user.profile, "phone_number"), Mock)
        self.user.profile.save.assert_not_called()

    def test_validate_otp_right_validation_code(self):
        """
        Test  the post  request to validate otp with good reqs.
        Expected behavior:
            - Check loggin validation msg
            - Check the response say success validate-otp.
            - Status code 201.
            - Check that user profile mock has the phone_number
            - Check that profile mock save method has called once.
        """
        correct_otp = "correct26"
        payload = {"phone_number": 3219990000, "one_time_password": correct_otp}
        url_endpoint = reverse(self.reverse_viewname)
        user_otp_key = f"{self.user.username}-{payload['phone_number']}"
        cache.set(user_otp_key, correct_otp, timeout=600)

        with self.assertLogs(views.__name__, level="INFO") as logs:
            response = self.client.post(url_endpoint, payload, format="json")

        self.assertEqual(logs.output, [
            f"INFO:{views.__name__}:validating otp for {user_otp_key[:-5]}*****"
        ])
        self.assertDictEqual(response.json(), {"message": "Success validate-otp! Saved phone_number"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.profile.phone_number, payload["phone_number"])
        self.user.profile.save.assert_called_once()
