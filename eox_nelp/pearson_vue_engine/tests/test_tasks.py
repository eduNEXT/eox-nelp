"""
This module contains unit tests for the tasks.py module and its functions.
"""
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from eox_nelp.pearson_vue_engine.tasks import real_time_import_task_v2

User = get_user_model()


class TestRealTimeImportTaskV2(TestCase):
    """
    Unit tests for the real_time_import_task_v2 function.
    """

    def setUp(self):
        """Set up a test user for the real-time import task."""
        self.user, _ = User.objects.get_or_create(username="vader")
        self.exam_id = "exam123"
        self.kwargs = {"extra_info": "test"}
        self.action_parameters = {
            "user_data": "test",
            "platform_data": "test",
            "exam_data": "test",
        }
        self.generate_action_parameters_patcher = patch("eox_nelp.pearson_vue_engine.tasks.generate_action_parameters")
        self.generate_action_parameters_mock = self.generate_action_parameters_patcher.start()
        self.generate_action_parameters_mock.return_value = self.action_parameters
        self.addCleanup(self.generate_action_parameters_patcher.stop)

    @patch("eox_nelp.pearson_vue_engine.tasks.update_user_engines")
    @patch("eox_nelp.pearson_vue_engine.tasks.PearsonEngineApiClient")
    def test_real_time_import_rti(self, mock_api_client, update_user_engines_mock):
        """Test real-time import action using the Pearson Engine API.

        Expected behavior:
            - update_user_engines is called with correct parameters.
            - The real_time_import method is called with the correct parameters.
        """
        mock_action = MagicMock()
        mock_action.return_value = {"error": False}
        mock_api_client.return_value = MagicMock(**{"real_time_import": mock_action})
        action_name = "rti"

        real_time_import_task_v2(self.user.id, action_name=action_name, **self.kwargs)

        update_user_engines_mock.assert_called_once_with(self.user, action_name, None)
        mock_action.assert_called_once_with(**self.action_parameters, **self.kwargs)

    @patch("eox_nelp.pearson_vue_engine.tasks.update_user_engines")
    @patch("eox_nelp.pearson_vue_engine.tasks.PearsonEngineApiClient")
    def test_real_time_import_cdd(self, mock_api_client, update_user_engines_mock):
        """Test candidate demographics import action using the Pearson Engine API.

        Expected behavior:
            - update_user_engines is called with correct parameters.
            - The import_candidate_demographics method is called with the correct parameters.
        """
        mock_action = MagicMock()
        mock_action.return_value = {"error": False}
        mock_api_client.return_value = MagicMock(**{"import_candidate_demographics": mock_action})
        action_name = "cdd"

        real_time_import_task_v2(self.user.id, action_name=action_name, **self.kwargs)

        update_user_engines_mock.assert_called_once_with(self.user, action_name, None)
        mock_action.assert_called_once_with(**self.action_parameters, **self.kwargs)

    @patch("eox_nelp.pearson_vue_engine.tasks.update_user_engines")
    @patch("eox_nelp.pearson_vue_engine.tasks.PearsonEngineApiClient")
    def test_real_time_import_ead(self, mock_api_client, update_user_engines_mock):
        """Test exam authorization import action using the Pearson Engine API.

        Expected behavior:
            - update_user_engines is called with correct parameters.
            - The import_exam_authorization method is called with the correct parameters.
        """
        mock_action = MagicMock()
        mock_action.return_value = {"error": False}
        mock_api_client.return_value = MagicMock(**{"import_exam_authorization": mock_action})
        action_name = "ead"

        real_time_import_task_v2(self.user.id, exam_id=self.exam_id, action_name=action_name, **self.kwargs)

        update_user_engines_mock.assert_called_once_with(self.user, action_name, self.exam_id,)
        mock_action.assert_called_once_with(**self.action_parameters, **self.kwargs)

    @patch("eox_nelp.pearson_vue_engine.tasks.update_user_engines")
    def test_real_time_import_invalid_action(self, update_user_engines_mock):
        """Test that a KeyError is raised for an invalid action name.

        Expected behavior:
            - KeyError is raised when an invalid action name is provided.
            - update_user_engines is not called
            - generate_action_parameters is not called
        """
        with self.assertRaises(KeyError):
            real_time_import_task_v2(self.user.id, action_name="invalid_action")
        update_user_engines_mock.assert_not_called()
        self.generate_action_parameters_mock.assert_not_called()

    @patch("eox_nelp.pearson_vue_engine.tasks.update_user_engines")
    @patch('eox_nelp.pearson_vue_engine.tasks.PearsonEngineApiClient')
    def test_real_time_import_user_not_found(self, mock_api_client, update_user_engines_mock):
        """Test that a DoesNotExist is raised for an invalid user id.

        Expected behavior:
            - update_user_engines is not called
            - PearsonEngineApiClient is not called
            - generate_action_parameters is not called
            - DoesNotExist is raised when an invalid user id is provided.
        """
        with self.assertRaises(User.DoesNotExist):
            real_time_import_task_v2(12345678, action_name="rti")
        mock_api_client.assert_not_called()
        update_user_engines_mock.assert_not_called()
        self.generate_action_parameters_mock.assert_not_called()

    @patch("eox_nelp.pearson_vue_engine.tasks.update_user_engines")
    @patch("eox_nelp.pearson_vue_engine.tasks.PearsonEngineApiClient")
    def test_raise_exception_on_error_response(self, mock_api_client, update_user_engines_mock):
        """Test that an exception is raised when the API response contains an Error.

        Expected behavior:
            - The exception is raised.
            - update_user_engines is called with correct parameters.
            - The action method is called with the correct parameters.
            - Exception contains the expected message.
        """
        mock_action = MagicMock()
        expected_message = "Timeout error"
        mock_action.return_value = {
            "error": True,
            "message": expected_message,
        }
        action_name = "rti"
        mock_api_client.return_value = MagicMock(**{"real_time_import": mock_action})
        with self.assertRaises(Exception) as context:
            real_time_import_task_v2(self.user.id, action_name=action_name, **self.kwargs)

        update_user_engines_mock.assert_called_once_with(self.user, action_name, None)
        mock_action.assert_called_once_with(**self.action_parameters, **self.kwargs)
        self.assertEqual(expected_message, str(context.exception))
