"""
This module contains unit tests for the tasks.py module and its functions.
"""
import unittest
from unittest.mock import MagicMock, call

from eox_nelp.pearson_vue.tasks import real_time_import_task  # Importa tu función aquí


class TestRealTimeImportTask(unittest.TestCase):
    """
    Unit tests for the real_time_import_task function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.mock_rti = MagicMock()
        self.mock_rti.run_pipeline.side_effect = lambda: None
        self.mock_rti_instance = MagicMock(return_value=self.mock_rti)

    def test_real_time_import_task_success(self):
        """
        Test real_time_import_task with successful execution of RTI pipeline.

        Expected behavior:
            - Task result is None.
            - Instance is initialized just once.
            - Method run_pipeline is called just once.
        """
        input_data = {
            "user_id": 5,
            "course_id": "course-v1:FutureX+guide+2023"
        }

        with unittest.mock.patch("eox_nelp.pearson_vue.tasks.RealTimeImport", self.mock_rti_instance):
            self.assertIsNone(real_time_import_task.apply(kwargs=input_data).get())

        self.mock_rti_instance.assert_called_once_with(pipeline_index=0, **input_data)
        self.mock_rti.run_pipeline.assert_called_once()

    def test_real_time_import_task_retry(self):
        """
        Test real_time_import_task with retry due to exception during RTI pipeline execution.

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

        with unittest.mock.patch("eox_nelp.pearson_vue.tasks.RealTimeImport", self.mock_rti_instance):
            real_time_import_task.apply(kwargs=input_data)

        self.mock_rti_instance.assert_has_calls([
            call(pipeline_index=0, **input_data),
            call(pipeline_index=0, **second_attempt_data),
        ])
        self.assertEqual(self.mock_rti.run_pipeline.call_count, 2)
