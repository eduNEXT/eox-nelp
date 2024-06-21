"""
Module to add managed exceptions related Pearson Vue Integration
"""


class PearsonBaseError(Exception):
    """Pearson Base error class
    Most classes that inherit from this class must have exception_type.
    """
    exception_type = "base-error"

    def __init__(self, *args):
        self.exception_type = self.exception_type
        super().__init__(self.exception_type, *args)


class PearsonKeyError(PearsonBaseError):
    """Pearson Key error class
    """
    exception_type = "key-error"

    def __init__(self, request_type, error_key, *args):
        self.request_type = request_type
        self.error_reason = error_key
        super().__init__(request_type, error_key, *args)


class PearsonAttributeError(PearsonBaseError):
    """Pearson Attribute error class
    """
    exception_type = "attribute-error"

    def __init__(self, request_type, attribute_error, *args):
        self.request_type = request_type
        self.attribute_error = attribute_error
        super().__init__(request_type, attribute_error, *args)


class PearsonValidationError(PearsonBaseError):
    """Pearson Validation error class
    """
    exception_type = "validation-error"

    def __init__(self, request_type, validation_exception, *args):
        self.request_type = request_type
        self.validation_exception = validation_exception
        super().__init__(request_type, validation_exception, *args)
