"""
Test file for eox_core views.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from mock import MagicMock, patch
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from eox_nelp.eox_core.api.v1.views import NelpEdxappUser

User = get_user_model()


class NelpEdxappUserTestCase(TestCase):
    """Test case for NelpEdxappUser view."""

    def setUp(self):
        """Set up test case."""
        self.view = NelpEdxappUser()
        self.factory = APIRequestFactory()
        self.mock_user = MagicMock(
            username='testuser',
            email='test@example.com',
            extrainfo=MagicMock(
                national_id='1234567890',
                arabic_name='اسم عربي',
                arabic_first_name='الاسم الأول',
                arabic_last_name='اسم العائلة'
            )
        )

        # Mock get_query_params to return request.GET
        patcher = patch.object(NelpEdxappUser, 'get_query_params', return_value={})
        self.mock_get_query_params = patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_user_query_with_username(self):
        """Test get_user_query method with username parameter.

        Expected behavior:
            - Returns query dict with username
            - Query contains the correct username
            - get_query_params is called exactly once with the request
        """
        request = self.factory.get('/')
        self.mock_get_query_params.return_value = {'username': 'testuser'}

        query = self.view.get_user_query(request)

        self.assertEqual(query, {'username': 'testuser'})
        self.mock_get_query_params.assert_called_once_with(request)

    def test_get_user_query_with_email(self):
        """Test get_user_query method with email parameter.

        Expected behavior:
            - Returns query dict with email
            - Query contains the correct email
            - get_query_params is called exactly once with the request
        """
        request = self.factory.get('/')
        self.mock_get_query_params.return_value = {'email': 'test@example.com'}

        query = self.view.get_user_query(request)

        self.assertEqual(query, {'email': 'test@example.com'})
        self.mock_get_query_params.assert_called_once_with(request)

    def test_get_user_query_with_national_id(self):
        """Test get_user_query method with national_id parameter.

        Expected behavior:
            - Returns query dict with extrainfo__national_id
            - Query contains the correct national_id in extrainfo format
            - get_query_params is called exactly once with the request
        """
        request = self.factory.get('/')
        self.mock_get_query_params.return_value = {'national_id': '1234567890'}

        query = self.view.get_user_query(request)

        self.assertEqual(query, {'extrainfo__national_id': '1234567890'})
        self.mock_get_query_params.assert_called_once_with(request)

    def test_get_user_query_no_params(self):
        """Test get_user_query method with no parameters.

        Expected behavior:
            - Raises ValidationError with correct error message
            - get_query_params is called exactly once with the request
        """
        request = self.factory.get('/')
        self.mock_get_query_params.return_value = {}

        with self.assertRaises(ValidationError) as context:
            self.view.get_user_query(request)

        self.assertEqual(context.exception.detail[0], 'Email or username or national_id needed')
        self.mock_get_query_params.assert_called_once_with(request)

    @patch('eox_nelp.eox_core.api.v1.views.get_object_or_404')
    @patch('eox_nelp.eox_core.api.v1.views.NelpUserReadOnlySerializer')
    def test_get_with_username(self, mock_serializer_class, mock_get_object):
        """Test get method with username parameter.

        Expected behavior:
            - Returns 200 status code
            - Returns serialized user data in expected format
            - get_object_or_404 is called with correct User model and username
            - Serializer class is instantiated
            - get_query_params is called exactly once with the request
        """
        mock_get_object.return_value = self.mock_user
        mock_serializer = MagicMock()
        mock_serializer.data = {'username': 'testuser', 'extrainfo': {'national_id': '1234567890'}}
        mock_serializer_class.return_value = mock_serializer
        self.mock_get_query_params.return_value = {'username': 'testuser'}
        request = self.factory.get('/')

        response = self.view.get(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'username': 'testuser', 'extrainfo': {'national_id': '1234567890'}})
        mock_get_object.assert_called_once_with(User, username='testuser')
        mock_serializer_class.assert_called_once()
        self.mock_get_query_params.assert_called_once_with(request)

    @patch('eox_nelp.eox_core.api.v1.views.get_object_or_404')
    @patch('eox_nelp.eox_core.api.v1.views.NelpUserReadOnlySerializer')
    def test_get_with_national_id(self, mock_serializer_class, mock_get_object):
        """Test get method with national_id parameter.

        Expected behavior:
            - Returns 200 status code
            - Returns serialized user data in expected format
            - get_object_or_404 is called with correct User model and national_id
            - Serializer class is instantiated
            - get_query_params is called exactly once with the request
        """
        mock_get_object.return_value = self.mock_user
        mock_serializer = MagicMock()
        mock_serializer.data = {'username': 'testuser', 'extrainfo': {'national_id': '1234567890'}}
        mock_serializer_class.return_value = mock_serializer
        self.mock_get_query_params.return_value = {'national_id': '1234567890'}
        request = self.factory.get('/')

        response = self.view.get(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'username': 'testuser', 'extrainfo': {'national_id': '1234567890'}})
        mock_get_object.assert_called_once_with(User, extrainfo__national_id='1234567890')
        mock_serializer_class.assert_called_once()
        self.mock_get_query_params.assert_called_once_with(request)
