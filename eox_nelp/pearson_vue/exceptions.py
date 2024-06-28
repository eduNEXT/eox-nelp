"""
Module to add managed exceptions related Pearson Vue Integration
"""
import inspect


class PearsonBaseError(Exception):
    """Pearson Base error class
    Most classes that inherit from this class must have exception_type.
    """
    exception_type = "base-error"

    def __init__(self, *args, pipe_frame=inspect.currentframe(), exception_reason="", exception_dict=None):
        """Init pearson exception using frame and exception_reason(str)
        Or init using exception_dict representation.
        That representation should have the following shape:
         exception_dict  = {
                'exception_type': 'validation-error',
                'pipe_args_dict': {
                    "cdd_request": {}
                },
                'pipe_function': 'validate_cdd_request',
                'exception_reason': "error: ['String to short.']"
            }
        """

        if exception_dict:
            _ = [setattr(self, key, value) for key, value in exception_dict.items()]
            super().__init__(exception_dict, *args)
        else:
            self.exception_type = self.exception_type
            arg_info = inspect.getargvalues(pipe_frame)
            self.pipe_args_dict = {arg: arg_info.locals[arg] for arg in arg_info.args}
            self.pipe_function = pipe_frame.f_code.co_name
            self.exception_reason = exception_reason
            super().__init__(self.to_dict(), *args)

    def to_dict(self):
        """
        Returns a dictionary representation of the class instance.

        Returns:
            A dictionary containing the instance's attributes as key-value pairs.
        """

        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    @classmethod
    def from_dict(cls, exception_dict: dict):
        """Create an instance of Person or its subclass from a dictionary.
            Returns:
            Matched instance of pearson exception subclass initialized.
            If not matched returns the base class initialized by default.
        """
        exception_type = exception_dict.get('exception_type')
        for subclass in cls.__subclasses__():
            if subclass.exception_type == exception_type:
                return subclass(exception_dict=exception_dict)

        # Default to Person if no matching subclass is found
        return cls()


class PearsonKeyError(PearsonBaseError):
    """Pearson Key error class
    """
    exception_type = "key-error"


class PearsonAttributeError(PearsonBaseError):
    """Pearson Attribute error class
    """
    exception_type = "attribute-error"


class PearsonValidationError(PearsonBaseError):
    """Pearson Validation error class
    """
    exception_type = "validation-error"
