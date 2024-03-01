"""Backend test abstraction."""
from mock import Mock


class RegistrationFormMock(Mock):
    """Class to inherit for test cases"""
    def get_registration_form(self, request):
        """Method to only exist in the super() call"""
        return Mock()


def get_registration_form_factory():
    """Return test class.
    Returns:
        Mock class.
    """
    return RegistrationFormMock


def get_views():
    """Return test class.
    Returns:
        Mock class.
    """
    return Mock()
