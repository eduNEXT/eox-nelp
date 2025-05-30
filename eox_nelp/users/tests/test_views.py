"""
Test file for users views.
"""
from unittest.mock import patch

from custom_reg_form.models import ExtraInfo
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from eox_nelp.users.api.v1.views import CoreEdxappUser

User = get_user_model()


class NelpEdxappUserTestCase(APITestCase):
    """Test case for NelpEdxappUser view."""

    def setUp(self):
        """Set up test case."""
        self.url = reverse('users:v1:edxapp-user')
        self.client = APIClient()

        # Create admin user for authentication
        self.client_user, _ = User.objects.get_or_create(username='test_admin', password='test123')
        self.client.force_authenticate(self.client_user)
        self.test_user, _ = User.objects.get_or_create(
            username='testuser',
            email='test@example.com',
            defaults={
                'is_active': True,
            },
        )
        self.test_user.extrainfo = ExtraInfo.objects.create(  # pylint: disable=no-member
            user=self.test_user,
            national_id='1234567890',
            arabic_name='اسم عربي',
            arabic_first_name='الاسم الأول',
            arabic_last_name='اسم العائلة',
        )

        # Patch authentication classes
        self.auth_patcher = patch.object(
            CoreEdxappUser,
            'authentication_classes',
            [],
        )
        self.auth_patcher.start()

        # Patch permission classes
        self.perm_patcher = patch.object(
            CoreEdxappUser,
            'permission_classes',
            [],
        )
        self.perm_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.auth_patcher.stop()
        self.perm_patcher.stop()
        super().tearDown()

    @patch('eox_nelp.users.api.v1.views.NelpUserReadOnlySerializer')
    def test_get_user_query_with_username(self, mock_serializer_class):
        """Test get_user_query method with username parameter.

        Expected behavior:
            - Returns 200 status code
            - Response data matches expected serialized user data
            - NelpUserReadOnlySerializer is instantiated once
        """
        serializer_data = {
            'username': self.test_user.username,
            'extrainfo': {'national_id': self.test_user.extrainfo.national_id},
        }
        mock_serializer_class.return_value.data = serializer_data

        response = self.client.get(f"{self.url}?username={self.test_user.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)
        mock_serializer_class.assert_called_once()

    @patch('eox_nelp.users.api.v1.views.NelpUserReadOnlySerializer')
    def test_get_user_query_with_email(self, mock_serializer_class):
        """Test get_user_query method with email parameter.

        Expected behavior:
            - Returns 200 status code
            - Response data matches expected serialized user data
            - NelpUserReadOnlySerializer is instantiated once
        """
        serializer_data = {
            'username': self.test_user.username,
            'email': self.test_user.email,
        }
        mock_serializer_class.return_value.data = serializer_data

        response = self.client.get(f"{self.url}?email={self.test_user.email}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)
        mock_serializer_class.assert_called_once()

    @patch('eox_nelp.users.api.v1.views.NelpUserReadOnlySerializer')
    def test_get_user_query_with_national_id(self, mock_serializer_class):
        """Test get_user_query method with national_id parameter.

        Expected behavior:
            - Returns 200 status code
            - Response data matches expected serialized user data
            - NelpUserReadOnlySerializer is instantiated once
        """
        serializer_data = {
            'username': self.test_user.username,
            'extrainfo': {'national_id': self.test_user.extrainfo.national_id},
        }
        mock_serializer_class.return_value.data = serializer_data

        response = self.client.get(f"{self.url}?national_id={self.test_user.extrainfo.national_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)
        mock_serializer_class.assert_called_once()

    def test_get_user_query_no_params(self):
        """Test get_user_query method with no parameters.

        Expected behavior:
            - Returns 400 Bad Request status code
            - Error message indicates missing required parameters
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), 'Email or username or national_id needed')

    def test_get_user_not_found(self):
        """Test get method when user is not found.

        Expected behavior:
            - Returns 404 Not Found status code
        """
        response = self.client.get(f"{self.url}?username=nonexistent")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
