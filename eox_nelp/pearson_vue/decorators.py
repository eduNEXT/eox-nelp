"""
Module to add decorators related Pearson Vue Integration
"""
import logging

from eox_nelp.utils import camel_to_snake

try:
    from eox_audit_model.decorators import audit_method, rename_function
except ImportError:
    def rename_function(name):  # pylint: disable=unused-argument
        """Identity rename_function"""
        return lambda x: x

    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x

logger = logging.getLogger(__name__)


def audit_backend(func):
    """Decorator that wraps a class method with a try-finally block.

    Args:
        func: The method to be decorated.

    Returns:
        A wrapper function that executes the decorated method with a try-finally block.
        Finally if there is backend_data, is logged after the execution.
    """
    def wrapper(self, *args, **kwargs):

        backend_name = self.__class__.__name__

        @audit_method(action=f"Backend Execution: {backend_name}")
        @rename_function(name=f"audit_backend_{camel_to_snake(backend_name)}")
        def audit_backend_manager(backend_data, **kwargs):
            logger.info(
                "Backend %s executed. \n backend_data: %s",
                backend_name,
                backend_data,
            )

        try:
            return func(self, *args, **kwargs)
        finally:
            if self.use_audit_backend and not self.backend_data.get("catched_pearson_error"):
                audit_backend_manager(backend_data=self.backend_data, **kwargs)

    return wrapper
