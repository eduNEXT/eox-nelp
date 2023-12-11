""" Test file for third_party_auth pipeline functions."""
from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.test import TestCase
from mock import Mock
from rest_framework import status

from eox_nelp.third_party_auth.pipeline import safer_associate_username_by_uid

User = get_user_model()


@ddt
class SaferAssociaciateUsernameUidTestCase(TestCase):
    """Test class for safer_associate_username_by_uid method"""

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

    def test_user_already_matched(self):
        """Test the pipeline method is called with already matched user.
        Expected behavior:
            - Return None.
        """
        pipe_output = safer_associate_username_by_uid(
            self.request, self.backend, self.details, self.response, user=self.user,
        )

        self.assertIsNone(pipe_output)

    def test_user_not_associated(self):
        """Test the pipeline method try to match with uid but there is not user with that username.
        Expected behavior:
            - Pipe method returns None.
            - Strategy storage get_user method is called with desired params.
        """
        test_uid = "1888222999"

        self.backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        self.backend.strategy.storage.user.get_user.return_value = None

        pipe_output = safer_associate_username_by_uid(self.request, self.backend, self.details, self.response)

        self.assertEqual(None, pipe_output)
        self.backend.strategy.storage.user.get_user.assert_called_with(username=test_uid)

    @data(
        {"is_staff": True, "username": "1222333444"},
        {"is_superuser": True, "username": "1222333555"},
    )
    def test_staff_user_return_forbidden(self, user_kwargs):
        """Test the pipeline method try to match with uid, the user with matched username exists
        but is staff or superuser.
        Expected behavior:
            - The pipe method returns an HttpResponseForbidden object.
            - The pipe method response has a 403 forbidden status.
            - Strategy storage get_user method is called with desired params.
        """
        test_uid = user_kwargs["username"]
        past_user, _ = User.objects.get_or_create(**user_kwargs)

        self.backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        self.backend.strategy.storage.user.get_user.return_value = past_user

        pipe_output = safer_associate_username_by_uid(self.request, self.backend, self.details, self.response)

        self.assertIsInstance(pipe_output, HttpResponseForbidden)
        self.assertEqual(status.HTTP_403_FORBIDDEN, pipe_output.status_code)
        self.backend.strategy.storage.user.get_user.assert_called_with(username=test_uid)

    def test_user_associate_username_with_uid(self):
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

        pipe_output = safer_associate_username_by_uid(self.request, self.backend, self.details, self.response)

        self.assertEqual({"user": past_user, "is_new": False}, pipe_output)
        self.backend.strategy.storage.user.get_user.assert_called_with(username=test_uid)
