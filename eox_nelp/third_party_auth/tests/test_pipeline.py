""" Test file for third_party_auth pipeline functions."""
from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.test import TestCase
from mock import Mock

from eox_nelp.third_party_auth.exceptions import EoxNelpAuthException
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

    def test_user_already_matched(self):
        """Test the pipeline method is called with already matched user.
        Expected behavior:
            - Return None.
        """
        backend = Mock()

        pipe_output = safer_associate_username_by_uid(backend, self.details, self.response, user=self.user)

        self.assertEqual(None, pipe_output)

    def test_user_not_associated(self):
        """Test the pipeline method try to match with uid but there is not user with that username.
        Expected behavior:
            - Pipe Return None.
            - Strategy storage get_user method is called with desired params.
        """
        test_uid = "1888222999"
        backend = Mock()
        backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        backend.strategy.storage.user.get_user.return_value = None

        pipe_output = safer_associate_username_by_uid(backend, self.details, self.response)

        self.assertEqual(None, pipe_output)
        backend.strategy.storage.user.get_user.assert_called_with(username=test_uid)

    @data(
        {"is_staff": True, "username": "1222333444"},
        {"is_superuser": True, "username": "1222333555"},
    )
    def test_staff_user_raise_exc(self, user_kwargs):
        """Test the pipeline method try to match with uid, the user with matched username exists
        but is staff or superuser.
        Expected behavior:
            - Raise EoxNelpAuthException exception
            - Strategy storage get_user method is called with desired params.
        """
        test_uid = user_kwargs["username"]
        past_user, _ = User.objects.get_or_create(**user_kwargs)
        backend = Mock()
        backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        backend.strategy.storage.user.get_user.return_value = past_user

        self.assertRaises(EoxNelpAuthException, safer_associate_username_by_uid, backend, self.details, self.response)
        backend.strategy.storage.user.get_user.assert_called_with(username=test_uid)

    def test_user_associate_username_with_uid(self):
        """Test the pipeline method try to match with uid, the user with matched username exists
        and is returned.
        Expected behavior:
            - Strategy storage get_user method is called with desired params.
            - The method return the desirect with `user` and `is_new` keys.
        """
        test_uid = "1777888999"
        past_user, _ = User.objects.get_or_create(
            username=test_uid,
        )
        backend = Mock()
        backend.get_idp.return_value.get_user_permanent_id.return_value = test_uid
        backend.strategy.storage.user.get_user.return_value = past_user

        pipe_output = safer_associate_username_by_uid(backend, self.details, self.response)

        self.assertEqual({"user": past_user, "is_new": False}, pipe_output)
        backend.strategy.storage.user.get_user.assert_called_with(username=test_uid)
