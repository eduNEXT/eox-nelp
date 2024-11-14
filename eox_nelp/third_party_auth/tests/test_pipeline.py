""" Test file for third_party_auth pipeline functions."""
from custom_reg_form.models import ExtraInfo
from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponseForbidden
from django.test import TestCase
from mock import Mock, patch
from rest_framework import status

from eox_nelp.third_party_auth import utils
from eox_nelp.third_party_auth.pipeline import (
    disallow_staff_superuser_users,
    safer_associate_user_by_national_id,
    safer_associate_user_by_social_auth_record,
    validate_national_id_and_associate_user,
)

User = get_user_model()


class SetUpPipeMixin:
    """Mixin for SetUp pipelines"""

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.details = {}
        self.response = {
            "idp_name": "tpa-saml-sso",
            "attributes": {},
        }
        self.user, _ = User.objects.get_or_create(username="vader")
        self.backend = Mock()
        self.request = Mock()

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        self.backend.reset_mock()
        self.request.reset_mock()


class SaferAssociateUserUsingUid(SetUpPipeMixin):
    """Mixin for pipes that match user using uid"""

    # pylint: disable=no-member
    def test_user_already_matched(self):
        """Test the pipeline method is called with already matched user.
        Expected behavior:
            - Return None.
        """
        pipe_output = self.uid_pipe(
            self.request, self.backend, self.details, self.response, user=self.user,
        )

        self.assertIsNone(pipe_output)

    def test_user_not_associated(self):
        """Test the pipeline method try to match with uid but there is not user with that match.
        Expected behavior:
            - Pipe method returns None.
            - Strategy storage get_user method is called with desired params.
        """
        test_uid = "1888222999"

        self.backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        self.backend.strategy.storage.user.get_user.return_value = None

        pipe_output = self.uid_pipe(self.request, self.backend, self.details, self.response)

        self.assertIsNone(pipe_output)
        self.backend.strategy.storage.user.get_user.assert_called_with(**{self.user_query: test_uid})

    def test_multiple_user_match(self):
        """Test the pipeline method try to match with uid but there are multiple matches.
        Expected behavior:
            - Expected logs of multiple returns
            - Pipe method returns None.
        """
        test_uid = "1888222999"

        self.backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        exc_msg = "return 7"
        self.backend.strategy.storage.user.get_user.side_effect = MultipleObjectsReturned(exc_msg)
        expected_log = [
            f"INFO:{utils.__name__}:"
            f"Pipeline tries to match user with uid({test_uid}) using {self.user_query}, "
            f"but Multiple users found: {exc_msg}"
        ]
        with self.assertLogs(utils.__name__, level="INFO") as logs:
            pipe_output = self.uid_pipe(self.request, self.backend, self.details, self.response)
            self.assertIsNone(pipe_output)
        self.assertListEqual(logs.output, expected_log)


class SaferAssociaciateUserByNationalIdTestCase(SaferAssociateUserUsingUid, TestCase):
    """Test case for `safer_associate_user_by_national_id` method"""
    uid_pipe = staticmethod(safer_associate_user_by_national_id)
    user_query = "extrainfo__national_id"

    def test_user_associate_uid_with_national_id(self):
        """Test the pipeline method try to match with uid, the user with matched username exists
        and is returned.
        Expected behavior:
            - Strategy storage get_user method is called with desired params.
            - The method returns the desirect with `user` and `is_new` keys.
        """
        test_uid = "1777888999"
        past_user, _ = User.objects.get_or_create(
            username=test_uid,
        )

        self.backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        self.backend.strategy.storage.user.get_user.return_value = past_user

        pipe_output = self.uid_pipe(self.request, self.backend, self.details, self.response)

        self.assertEqual({"user": past_user, "is_new": False}, pipe_output)
        self.backend.strategy.storage.user.get_user.assert_called_with(**{self.user_query: test_uid})


class SaferAssociaciateUserBySocialAuthRecordTestCase(SaferAssociateUserUsingUid, TestCase):
    """Test case for `safer_associate_user_by_social_auth_record`"""
    uid_pipe = staticmethod(safer_associate_user_by_social_auth_record)
    user_query = "social_auth__uid__endswith"

    def test_user_associate_uid_with_social_record(self):
        """Test the pipeline method try to match with uid, the user with matched query exists
        and is returned.
        Expected behavior:
            - Strategy storage get_user method is called with desired params.
            - The method returns the desirect with `user` and `is_new` keys.
        """
        test_uid = "1777888999"
        past_user, _ = User.objects.get_or_create(
            username=test_uid,
        )

        self.backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        self.backend.strategy.storage.user.get_user.return_value = past_user

        pipe_output = self.uid_pipe(
            self.request,
            self.backend,
            self.details,
            self.response,
        )

        self.assertEqual({"user": past_user, "is_new": False}, pipe_output)
        self.backend.strategy.storage.user.get_user.assert_called_with(**{self.user_query: test_uid})


@ddt
class DisallowStaffSuperuserUsersTestCase(SetUpPipeMixin, TestCase):
    """Test class for pipe `disallow_staff_superusers_users`"""
    @data(
        {"is_staff": True, "username": "1222333444"},
        {"is_superuser": True, "username": "1222333555"},
    )
    def test_staff_user_return_forbidden(self, user_queries):
        """Test the pipeline receive a not allower staff or superuser.
        Expected behavior:
            - The pipe method returns an HttpResponseForbidden object.
            - The pipe method response has a 403 forbidden status.
        """
        past_user, _ = User.objects.get_or_create(**user_queries)

        pipe_output = disallow_staff_superuser_users(
            self.request,
            self.backend,
            self.details,
            self.response,
            user=past_user
        )

        self.assertIsInstance(pipe_output, HttpResponseForbidden)
        self.assertEqual(status.HTTP_403_FORBIDDEN, pipe_output.status_code)

    def test_not_user_arg(self):
        """Test the pipeline method doesnt receive user
        Expected behavior:
            - The pipe method returns None
        """

        pipe_output = disallow_staff_superuser_users(self.request, self.backend, self.details, self.response)

        self.assertIsNone(pipe_output)

    def test_not_staff_or_superuser_user(self):
        """Test the pipeline method receives a normal user(not staff and not superuser)
        Expected behavior:
            - The pipe method returns empty dict
        """
        past_user, _ = User.objects.get_or_create(username="notstaffsuperuser")

        pipe_output = disallow_staff_superuser_users(
            self.request,
            self.backend,
            self.details,
            self.response,
            user=past_user
        )

        self.assertDictEqual({}, pipe_output)


class ValidateNationalIdAndAssociateUserTestCase(SetUpPipeMixin, TestCase):
    """Test case for `validate_national_id_and_associate_user` pipeline"""

    def test_associate_user_when_national_id_matches_uid(self):
        """Test that the user is associated if the national ID matches the UID suffix.

        Expected behavior:
            - Calls the original social_core_associate_user function.
        """
        self.user.extrainfo = ExtraInfo(arabic_name="فيدر", national_id="1234567890")
        test_uid = "test-saml:1234567890"
        social_auth = Mock(user=self.user)
        self.backend.strategy.storage.user.create_social_auth.return_value = social_auth

        pipe_output = validate_national_id_and_associate_user(self.request, self.backend, test_uid, user=self.user)

        self.assertEqual(pipe_output, {"user": self.user, "new_association": True, "social": social_auth})

    @patch("eox_nelp.third_party_auth.pipeline.logout")
    def test_redirect_to_register_when_national_id_does_not_match(self, mock_logout):
        """Test that user is logged out and redirected if the national ID doesn't match UID.

        Expected behavior:
            - Calls logout on the request.
            - Returns redirect with status code 302
            - Redirects to the registration page.
        """
        self.user.extrainfo = ExtraInfo(arabic_name="فيدر", national_id="1452487963")
        test_uid = "test-saml:1234567890"

        pipe_output = validate_national_id_and_associate_user(self.request, self.backend, test_uid, user=self.user)

        mock_logout.assert_called_once_with(self.request)
        self.assertEqual(pipe_output.status_code, 302)
        self.assertEqual(pipe_output.url, "/register")

    @patch("eox_nelp.third_party_auth.pipeline.logout")
    def test_redirect_when_user_has_no_national_id(self, mock_logout):
        """Test that user is redirected if no national ID is found on user.
        Expected behavior:
            - Calls logout on the request.
            - Returns redirect with status code 302
            - Redirects to the registration page.
        """
        setattr(self.user, "extrainfo", None)
        test_uid = "1777888999"

        pipe_output = validate_national_id_and_associate_user(self.request, self.backend, test_uid, user=self.user)

        mock_logout.assert_called_once_with(self.request)
        self.assertEqual(pipe_output.status_code, 302)
        self.assertEqual(pipe_output.url, "/register")
