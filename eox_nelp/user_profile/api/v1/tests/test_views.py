"""This file contains all the test for the user_profile API V1 views.py file.

Classes:
    UpdateUserDataTestCase: Class to test update_user_data view
"""

from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from eox_nelp.edxapp_wrapper.user_api import accounts, errors
from eox_nelp.tests.mixins import POSTAuthenticatedTestMixin
from eox_nelp.user_profile.api.v1 import views

User = get_user_model()


@ddt
class UpdateUserDataTestCase(POSTAuthenticatedTestMixin, APITestCase):
    """Test case for update user data view."""
    reverse_viewname = "user-profile-api:v1:update-user-data"

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset Mocks"""
        accounts.reset_mock()
        accounts.api.update_account_settings.side_effect = None

    @data({}, {"not_phone_number": 3123123123}, {"not_one_time_password": 12345678, "phone_number": 3123123123})
    def test_validate_otp_without_right_payload(self, wrong_payload):
        """
        Test  the post request to validate otp is not running due missing keys in the payload sent.
        Expected behavior:
            - Check the response say is missing some keys.
            - Status code 400.
            - Check that update_account_settings method has not been called.
        """
        url_endpoint = reverse(self.reverse_viewname)

        response = self.client.post(url_endpoint, wrong_payload, format="json")

        self.assertDictEqual(response.json(), {"detail": "missing phone_number or one_time_password in data."})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        accounts.api.update_account_settings.assert_not_called()

    def test_validate_otp_without_right_validation_code(self):
        """
        Test  the post request to validate otp with wrong validation code.
        Expected behavior:
            - Check logging validation msg
            - Status code 403.
            - Check that update_account_settings method has not been called.
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
        accounts.api.update_account_settings.assert_not_called()

    def test_validate_otp_right_validation_code(self):
        """
        Test  the post  request to validate otp with good reqs.
        Expected behavior:
            - Check loggin validation msg
            - Check the response say success validate-otp.
            - Status code 200.
            - Check that update_account_settings method has called once.
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
        self.assertDictEqual(response.json(), {"message": "User's fields has been updated successfully"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        accounts.api.update_account_settings.assert_called_once_with(self.user, payload)

    def test_account_validation_error(self):
        """
        Test that a bad request is returned when an AccountValidationError is raised.

        Expected behavior:
            - Check logging validation msg
            - Check the response contains fields_errors.
            - Status code 400.
            - Check that update_account_settings method has called once.
        """
        correct_otp = "correct26"
        payload = {"phone_number": 3219990000, "one_time_password": correct_otp}
        url_endpoint = reverse(self.reverse_viewname)
        user_otp_key = f"{self.user.username}-{payload['phone_number']}"
        cache.set(user_otp_key, correct_otp, timeout=600)
        accounts.api.update_account_settings.side_effect = errors.AccountValidationError(
            field_errors="Invalid phone number",
        )

        with self.assertLogs(views.__name__, level="INFO") as logs:
            response = self.client.post(url_endpoint, payload, format="json")

        self.assertEqual(logs.output, [
            f"INFO:{views.__name__}:validating otp for {user_otp_key[:-5]}*****"
        ])
        self.assertDictEqual(response.json(), {"field_errors": "Invalid phone number"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        accounts.api.update_account_settings.assert_called_once_with(self.user, payload)

    def test_account_update_error(self):
        """
        Test that a bad request is returned when an AccountUpdateError is raised.

        Expected behavior:
            - Check logging validation msg
            - Check the response contains developer and user message.
            - Status code 400.
            - Check that update_account_settings method has called once.
        """
        correct_otp = "correct26"
        payload = {"phone_number": 3219990000, "one_time_password": correct_otp}
        url_endpoint = reverse(self.reverse_viewname)
        user_otp_key = f"{self.user.username}-{payload['phone_number']}"
        cache.set(user_otp_key, correct_otp, timeout=600)
        expected_response = {
            "developer_message": "The testing method failed",
            "user_message": "You user wasn't updated",
        }
        accounts.api.update_account_settings.side_effect = errors.AccountUpdateError(
            **expected_response,
        )

        with self.assertLogs(views.__name__, level="INFO") as logs:
            response = self.client.post(url_endpoint, payload, format="json")

        self.assertEqual(logs.output, [
            f"INFO:{views.__name__}:validating otp for {user_otp_key[:-5]}*****"
        ])
        self.assertDictEqual(response.json(), expected_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        accounts.api.update_account_settings.assert_called_once_with(self.user, payload)
