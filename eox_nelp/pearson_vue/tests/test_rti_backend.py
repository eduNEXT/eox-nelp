"""
This module contains unit tests for the RealTimeImport class and its methods in rti_backend.py.
"""
import inspect
import unittest
from unittest.mock import MagicMock, call, patch

from ddt import data, ddt

from eox_nelp.pearson_vue import decorators
from eox_nelp.pearson_vue.exceptions import PearsonAttributeError, PearsonKeyError, PearsonValidationError
from eox_nelp.pearson_vue.rti_backend import (
    CandidateDemographicsDataImport,
    ErrorRealTimeImportHandler,
    ExamAuthorizationDataImport,
    RealTimeImport,
    ResultNotificationBackend,
)


class TestAbstractBackendMixin:
    """
    Unit tests for the AbstracBackend subclasses.
    """

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set up the test environment.
        """
        self.backend_data = {"pipeline_index": 0}
        self.rti = self.rti_backend_class(**self.backend_data)

    def test_init(self):
        """
        Test the initialization of the RealTimeImport class.

        Expected behavior:
            - Instance backend_data is the same as the initialization data.
        """
        self.assertDictEqual(self.rti.backend_data, self.backend_data)

    def test_run_pipeline(self):
        """
        Test the execution of the RTI pipeline.

        Expected behavior:
            - Pipeline method 1 is called with the original data.
            - Pipeline method 2 is called with updated data.
            - backend_data attribute is the expected value.
            - assert logs if the class has truthy `use_audit_backend`
        """
        # Mock pipeline functions
        func1 = MagicMock(return_value={"updated_key": "value1"})
        func2 = MagicMock(return_value={"additional_key": "value2"})
        self.rti.get_pipeline = MagicMock(return_value=[func1, func2])

        if self.rti.use_audit_backend:
            with self.assertLogs(decorators.__name__, level="INFO") as logs:
                self.rti.run_pipeline()
            self.assertEqual(
                logs.output,
                [
                    f"INFO:{decorators.__name__}:"
                    f"Backend {self.rti.__class__.__name__} executed. \n backend_data: {self.rti.backend_data}"
                ]
            )
        else:
            self.rti.run_pipeline()

        func1.assert_called_once_with(**self.backend_data)
        func2.assert_called_once_with(**{"updated_key": "value1", "pipeline_index": 1})
        self.assertDictEqual(
            self.rti.backend_data,
            {
                "pipeline_index": len(self.rti.get_pipeline()) - 1,  # includes total of pipeline methods
                **func1(),  # Include data from func1
                **func2(),  # Include data from func2
            },
        )

    def test_pipeline_index(self):
        """
        Test that the pipeline start from the pipeline_index position.

        Expected behavior:
            - Pipeline method 1 is called once.
            - Pipeline method 2 is called once.
            - Pipeline method 3 is called twice
            - backend_data attribute is the expected value.
        """
        # Mock pipeline functions
        func1 = MagicMock(return_value={"updated_key": "value1"})
        func2 = MagicMock(return_value={"additional_key": "value2"})
        func3 = MagicMock()
        func3_output = {"last_value": "value3"}
        func3.side_effect = [Exception("Test exception"), func3_output]
        rti = self.rti_backend_class(pipeline_index=0)
        rti.get_pipeline = MagicMock(return_value=[func1, func2, func3])

        with self.assertRaises(Exception):
            # Running first time until the func3 raises an exception
            rti.run_pipeline()

        # This execution only runs the third method
        rti.run_pipeline()

        func1.assert_called_once_with(**{"pipeline_index": 0})
        func2.assert_called_once_with(**{"updated_key": "value1", "pipeline_index": 1})
        func3.assert_has_calls([
            call(**{"updated_key": "value1", "additional_key": "value2", "pipeline_index": 2}),
            call(**{"updated_key": "value1", "additional_key": "value2", "pipeline_index": 2}),
        ])
        self.assertDictEqual(
            rti.backend_data,
            {
                "pipeline_index": len(rti.get_pipeline()) - 1,  # includes total of pipeline methods
                **func1(),  # Include data from func1
                **func2(),  # Include data from func2
                **func3_output,  # Include data from func3
            },
        )

    def test_get_pipeline(self):
        """
        Test the retrieval of the RTI pipeline.

        Expected behavior:
            - Method return a list instance
            - All the pipeline items are callable.
        """
        pipeline = self.rti.get_pipeline()

        self.assertIsInstance(pipeline, list)
        self.assertTrue(all(callable(func) for func in pipeline))


@ddt
class TestRealTimeImport(TestAbstractBackendMixin, unittest.TestCase):
    """
    Unit tests for the RealTimeImport class.
    """
    rti_backend_class = RealTimeImport

    @patch("eox_nelp.pearson_vue.decorators.logger")
    @patch("eox_nelp.pearson_vue.tasks.rti_error_handler_task")
    @data(
        PearsonValidationError(inspect.currentframe(), "error: ['String to short.']"),
        PearsonKeyError(inspect.currentframe(), "eligibility_appt_date_first"),
        PearsonAttributeError(inspect.currentframe(), "Settings' object has no attribute PERITA")
    )
    def test_launch_validation_error_pipeline(self, pearson_error, rti_error_handler_task_mock, audit_logger):
        """
        Test the execution of the RTI finished after the second function call due
        `launch_validation_error_pipeline` kwarg.

        Expected behavior:
            - Pipeline method 1 is called with the original data.
            - Pipeline method 2 is called with updated data.
            - Pipeline method 3 is not called.
            - Pipeline method 4 is not called.
            - backend_data attribute is the expected value.
                Without func3,func4 data and pipeline index in the last.
            - rti_error_handler_task is called with executed__pipeline_kwargs and error_validation_kwargs.
            - audit_method_mock is not called due catched_pearson_error.
        """
        # Mock pipeline functions
        func1 = MagicMock(return_value={"updated_key": "value1"})
        func1.__name__ = "first_function"
        func2 = MagicMock()
        func2.side_effect = pearson_error
        func2.__name__ = "failed_function"
        func3 = MagicMock(return_value={"additional_key": "value3"})
        func4 = MagicMock(return_value={"additional_key": "value4"})
        executed_pipeline_kwargs = {
            "updated_key": "value1",
        }

        self.rti.get_pipeline = MagicMock(return_value=[func1, func2, func3, func4])
        self.rti.run_pipeline()

        func1.assert_called_once_with(**self.backend_data)
        func2.assert_called_once_with(pipeline_index=1, **executed_pipeline_kwargs)
        func3.assert_not_called()
        func4.assert_not_called()
        self.assertDictEqual(
            self.rti.backend_data,
            {
                "pipeline_index": 1,  # includes the pipe executed until break due exception
                'catched_pearson_error': True,  # pipeline error flag
                **func1(),  # Include data from func1 ()
            },
        )
        rti_error_handler_task_mock.delay.assert_called_with(
            failed_step_pipeline=func2.__name__,
            exception_dict=pearson_error.to_dict(),
            user_id=None,
            course_id=None,
        )
        audit_logger.info.assert_not_called()


class TestExamAuthorizationDataImport(TestRealTimeImport):
    """
    Unit tests for the rti_backend class.
    """
    rti_backend_class = ExamAuthorizationDataImport


class TestCandidateDemographicsDataImport(TestRealTimeImport):
    """
    Unit tests for the rti_backend class.
    """
    rti_backend_class = CandidateDemographicsDataImport


class TestErrorRealTimeImportHandler(TestAbstractBackendMixin, unittest.TestCase):
    """
    Unit tests for the rti_backend class.
    """
    rti_backend_class = ErrorRealTimeImportHandler


class TestResultNotificationBackend(TestRealTimeImport):
    """
    Unit tests for the ResultNotificationBackend class.
    """
    rti_backend_class = ResultNotificationBackend
