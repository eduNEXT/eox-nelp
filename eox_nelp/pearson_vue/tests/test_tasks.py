"""
This module contains unit tests for the tasks.py module and its functions.
"""
import unittest
from unittest.mock import MagicMock, call, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from eox_nelp.pearson_vue.tasks import (
    cdd_task,
    ead_task,
    real_time_import_task,
    real_time_import_task_v2,
    rti_error_handler_task,
)

User = get_user_model()


class TestRealTimeImportTask(unittest.TestCase):
    """
    Unit tests for the real_time_import_task function.
    """
    import_class_patch = "eox_nelp.pearson_vue.tasks.RealTimeImport"
    import_task_function = real_time_import_task

    def setUp(self):
        """
        Set up the test environment.
        """
        self.mock_rti = MagicMock()
        self.mock_rti.run_pipeline.side_effect = lambda: None
        self.mock_rti_instance = MagicMock(return_value=self.mock_rti)

    def test_import_task_success(self):
        """
        Test import task function with successful execution of RTI pipeline.

        Expected behavior:
            - Task result is None.
            - Instance is initialized just once.
            - Method run_pipeline is called just once.
        """
        input_data = {
            "user_id": 5,
            "course_id": "course-v1:FutureX+guide+2023"
        }
        with unittest.mock.patch(self.import_class_patch, self.mock_rti_instance):
            self.assertIsNone(self.import_task_function.apply(kwargs=input_data).get())

        self.mock_rti_instance.assert_called_once_with(pipeline_index=0, **input_data)
        self.mock_rti.run_pipeline.assert_called_once()

    def test__import_task_retry(self):
        """
        Test import task function with retry due to exception during RTI pipeline execution.

        Expected behavior:
            - Instance is initialized twice with variable data.
            - Method run_pipeline is called twice
        """
        input_data = {
            "user_id": 5,
            "course_id": "course-v1:FutureX+guide+2023"
        }
        second_attempt_data = {
            "user_id": 5,
            "course_id": "course-v1:FutureX+guide+2023",
            "email": "admin@example.com",
        }
        mock_exception = Exception("Test exception")
        self.mock_rti.run_pipeline.side_effect = [mock_exception, None]
        self.mock_rti.backend_data = second_attempt_data

        with unittest.mock.patch(self.import_class_patch, self.mock_rti_instance):
            self.import_task_function.apply(kwargs=input_data)

        self.mock_rti_instance.assert_has_calls([
            call(pipeline_index=0, **input_data),
            call(pipeline_index=0, **second_attempt_data),
        ])
        self.assertEqual(self.mock_rti.run_pipeline.call_count, 2)


class TestEadTask(TestRealTimeImportTask):
    """
    Unit tests for the ead_task function.
    """
    import_class_patch = "eox_nelp.pearson_vue.tasks.ExamAuthorizationDataImport"
    import_task_function = ead_task


class TestCddTask(TestRealTimeImportTask):
    """
    Unit tests for the cdd_task function.
    """
    import_class_patch = "eox_nelp.pearson_vue.tasks.CandidateDemographicsDataImport"
    import_task_function = cdd_task


class TestErrorValidationTask(TestRealTimeImportTask):
    """
    Unit tests for the cdd_task function.
    """
    import_class_patch = "eox_nelp.pearson_vue.tasks.ErrorRealTimeImportHandler"
    import_task_function = rti_error_handler_task


class TestRealTimeImportTaskV2(TestCase):
    """
    Unit tests for the real_time_import_task_v2 function.
    """

    def setUp(self):
        """Set up a test user for the real-time import task."""
        self.user, _ = User.objects.get_or_create(username="vader")
        self.exam_id = "exam123"
        self.kwargs = {"extra_info": "test"}

    @patch("eox_nelp.pearson_vue.tasks.PearsonEngineApiClient")
    def test_real_time_import_rti(self, mock_api_client):
        """Test real-time import action using the Pearson Engine API.

        Expected behavior:
            - The real_time_import method is called with the correct parameters.
        """
        mock_action = MagicMock()
        mock_action.return_value = {"error": False}
        mock_api_client.return_value = MagicMock(**{"real_time_import": mock_action})

        real_time_import_task_v2(self.user.id, action_name="rti", **self.kwargs)

        mock_action.assert_called_once_with(user=self.user, exam_id=None, **self.kwargs)

    @patch("eox_nelp.pearson_vue.tasks.PearsonEngineApiClient")
    def test_real_time_import_cdd(self, mock_api_client):
        """Test candidate demographics import action using the Pearson Engine API.

        Expected behavior:
            - The import_candidate_demographics method is called with the correct parameters.
        """
        mock_action = MagicMock()
        mock_action.return_value = {"error": False}
        mock_api_client.return_value = MagicMock(**{"import_candidate_demographics": mock_action})

        real_time_import_task_v2(self.user.id, action_name="cdd", **self.kwargs)

        mock_action.assert_called_once_with(user=self.user, exam_id=None, **self.kwargs)

    @patch("eox_nelp.pearson_vue.tasks.PearsonEngineApiClient")
    def test_real_time_import_ead(self, mock_api_client):
        """Test exam authorization import action using the Pearson Engine API.

        Expected behavior:
            - The import_exam_authorization method is called with the correct parameters.
        """
        mock_action = MagicMock()
        mock_action.return_value = {"error": False}
        mock_api_client.return_value = MagicMock(**{"import_exam_authorization": mock_action})

        real_time_import_task_v2(self.user.id, exam_id=self.exam_id, action_name="ead", **self.kwargs)

        mock_action.assert_called_once_with(user=self.user, exam_id=self.exam_id, **self.kwargs)

    def test_real_time_import_invalid_action(self):
        """Test that a KeyError is raised for an invalid action name.

        Expected behavior:
            - KeyError is raised when an invalid action name is provided.
        """
        with self.assertRaises(KeyError):
            real_time_import_task_v2(self.user.id, action_name="invalid_action")

    @patch('eox_nelp.pearson_vue.tasks.PearsonEngineApiClient')
    def test_real_time_import_user_not_found(self, mock_api_client):  # pylint: disable=unused-argument
        """Test that a DoesNotExist is raised for an invalid user id.

        Expected behavior:
            - DoesNotExist is raised when an invalid usser id is provided.
        """
        with self.assertRaises(User.DoesNotExist):
            real_time_import_task_v2(12345678, action_name="rti")

    @patch("eox_nelp.pearson_vue.tasks.PearsonEngineApiClient")
    def test_raise_exception_on_error_response(self, mock_api_client):
        """Test that an exception is raised when the API response contains an Error.

        Expected behavior:
            - The exception is raised.
            - The action method is called with the correct parameters.
            - Exception contains the expected message.
        """
        mock_action = MagicMock()
        expected_message = "Timeout error"
        mock_action.return_value = {
            "error": True,
            "message": expected_message,
        }
        mock_api_client.return_value = MagicMock(**{"real_time_import": mock_action})

        with self.assertRaises(Exception) as context:
            real_time_import_task_v2(self.user.id, action_name="rti", **self.kwargs)

        mock_action.assert_called_once_with(user=self.user, exam_id=None, **self.kwargs)
        self.assertEqual(expected_message, str(context.exception))
