"""
This module contains unit tests for the RealTimeImport class and its methods in rti_backend.py.
"""
import unittest
from unittest.mock import MagicMock, call

from eox_nelp.pearson_vue.rti_backend import RealTimeImport


class TestRealTimeImport(unittest.TestCase):
    """
    Unit tests for the RealTimeImport class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.backend_data = {"pipeline_index": 0}
        self.rti = RealTimeImport(**self.backend_data)

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
        """
        # Mock pipeline functions
        func1 = MagicMock(return_value={"updated_key": "value1"})
        func2 = MagicMock(return_value={"additional_key": "value2"})
        self.rti.get_pipeline = MagicMock(return_value=[func1, func2])

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
        rti = RealTimeImport(pipeline_index=0)
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

    def test_safely_pipeline_termination(self):
        """
        Test the execution of the RTI finished after the second function call due
        `safely_pipeline_termination` kwarg.

        Expected behavior:
            - Pipeline method 1 is called with the original data.
            - Pipeline method 2 is called with updated data.
            - Pipeline method 3 is not called.
            - Pipeline method 4 is not called.
            - backend_data attribute is the expected value.
                Without func3,func4 data and pipeline index in the last.
        """
        # Mock pipeline functions
        func1 = MagicMock(return_value={"updated_key": "value1"})
        func2 = MagicMock(return_value={"safely_pipeline_termination": True})
        func3 = MagicMock(return_value={"additional_key": "value3"})
        func4 = MagicMock(return_value={"additional_key": "value4"})

        self.rti.get_pipeline = MagicMock(return_value=[func1, func2, func2])

        self.rti.run_pipeline()

        func1.assert_called_once_with(**self.backend_data)
        func2.assert_called_once_with(**{"updated_key": "value1", "pipeline_index": 1})
        func3.assert_not_called()
        func4.assert_not_called()

        self.assertDictEqual(
            self.rti.backend_data,
            {
                "pipeline_index": len(self.rti.get_pipeline()) - 1,  # includes total of pipeline methods
                **func1(),  # Include data from func1 ()
                **func2(),  # Include data from func2  (with safely_pipeline_termination)
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
