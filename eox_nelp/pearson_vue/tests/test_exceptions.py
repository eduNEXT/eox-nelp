"""
This module contains unit tests for the RealTimPearsonBaseError class and its methods in exception.py.
"""
import unittest
from unittest.mock import MagicMock, Mock, patch

from ddt import data, ddt

from eox_nelp.pearson_vue.exceptions import (
    PearsonAttributeError,
    PearsonBaseError,
    PearsonKeyError,
    PearsonValidationError,
)


@ddt
class PearsonBaseErrorTest(unittest.TestCase):
    """Class to test the PearsonBaseError class"""
    def test_init_with_exception_reason(self):
        """Tests initialization with a simple exception reason string.
        Expected behavior:
            - Atribute exception_type of exception class is the expected.
            - Atribute exception_reason of exception class is the expected.
            - Atribute pipe_args_dict of exception class is the expected.
            - Atribute pipe_function of exception class is the expected.
        """

        exception_reason = "Test error message"

        error = PearsonBaseError(exception_reason)

        self.assertEqual(error.exception_type, "base-error")
        self.assertEqual(error.exception_reason, exception_reason)
        self.assertIsNone(error.pipe_args_dict)
        self.assertIsNone(error.pipe_function)

    @patch("eox_nelp.pearson_vue.exceptions.inspect")
    def test_init_with_pipe_frame(self, inspect_mock):
        """Tests initialization using a pipe function frame.
        Expected behavior:
            - Atribute exception_type of exception class is the expected.
            - Atribute exception_reason of exception class is the expected.
            - Atribute pipe_args_dict of exception class is the expected.
            - Atribute pipe_function of exception class is the expected.
        """
        mock_arg_info = MagicMock(
            locals={"arg1": "value1", "arg2": "value2", "arg3": "value3"},
            args=["arg1", "arg2"],
        )
        inspect_mock.getargvalues.return_value = mock_arg_info
        pipe_frame_mock = Mock()
        pipe_frame_mock.f_code.co_name = "mock_pipe_function"

        error = PearsonBaseError("Test error", pipe_frame=pipe_frame_mock)

        self.assertEqual(error.exception_type, "base-error")
        self.assertEqual(error.exception_reason, "Test error")
        self.assertEqual(error.pipe_args_dict, {"arg1": "value1", "arg2": "value2"})
        self.assertEqual(error.pipe_function, "mock_pipe_function")

    def test_init_with_pipe_args_dict_and_pipe_function(self):
        """Tests initialization with explicit pipe arguments and function.
        Expected behavior:
            - Atribute  exception_type of exception class is the expected.
            - Atribute  exception_reason of exception class is the expected.
            - Atribute  pipe_args_dict of exception class is the expected.
            - Atribute  pipe_function of exception class is the expected.
        """

        pipe_args_dict = {"key1": "value1", "key2": "value2"}
        pipe_function = "my_pipe_function"

        error = PearsonBaseError(
            "Test error", pipe_args_dict=pipe_args_dict, pipe_function=pipe_function
        )

        self.assertEqual(error.exception_type, "base-error")
        self.assertEqual(error.exception_reason, "Test error")
        self.assertEqual(error.pipe_args_dict, pipe_args_dict)
        self.assertEqual(error.pipe_function, pipe_function)

    def test_to_dict(self):
        """Tests conversion of the object to a dictionary.
        Expected behavior:
            - to_dict representation is equivalent to dict used to generate the exception
        """

        exception_dict = {
            "exception_type": "base-error",
            "pipe_args_dict": {"cdd_request": {}},
            "pipe_function": "validate_cdd_request",
            "exception_reason": "error: ['String to short.']",
        }

        error = PearsonBaseError(**exception_dict)

        self.assertEqual(error.to_dict(), exception_dict)

    def test_from_dict_base_class(self):
        """Tests creating a PearsonBaseError instance from a dictionary (base class).
        Expected behavior:
            - from dict method return the PearsonBaseError instance.
            - Atribute  exception_type of exception class is the expected.(base due not match)
            - Atribute  exception_reason of exception class is the expected.
            - Atribute  pipe_args_dict of exception class is the expected.
            - Atribute  pipe_function of exception class is the expected.
        """

        exception_dict = {
            "exception_type": "unmatching-error",
            "pipe_args_dict": {"cdd_request": {}},
            "pipe_function": "validate_cdd_request",
            "exception_reason": "error: ['String to short.']",
        }

        error = PearsonBaseError.from_dict(exception_dict)

        self.assertIsInstance(error, PearsonBaseError)
        self.assertEqual(error.exception_type, PearsonBaseError.exception_type)
        self.assertEqual(error.exception_reason, exception_dict["exception_reason"])
        self.assertEqual(error.pipe_args_dict, exception_dict["pipe_args_dict"])
        self.assertEqual(error.pipe_function, exception_dict["pipe_function"])

    @data(PearsonAttributeError, PearsonKeyError, PearsonValidationError)
    def test_from_dict_subclass(self, subclass_expected):
        """Tests creating a subclass instance from a dictionary (subclass).
        Expected behavior:
            - from dict method return the PearsonSubclassinstance.
            - to_dict representation is equivalent to dict used to generate the exception
        """
        exception_dict = {
            "exception_type": subclass_expected.exception_type,
            "pipe_args_dict": {"cdd_request": {}},
            "pipe_function": "validate_cdd_request",
            "exception_reason": "error: some reason explaining the error xD",
        }

        error = PearsonBaseError.from_dict(exception_dict)

        self.assertIsInstance(error, subclass_expected)
        self.assertEqual(error.to_dict(), exception_dict)  # Check all attributes
