"""
This module contains unit tests for the RealTimeImport class and its methods in rti_backend.py.
"""
import unittest
from unittest.mock import MagicMock

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
