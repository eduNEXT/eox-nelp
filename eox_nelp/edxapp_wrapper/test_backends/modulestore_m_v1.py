"""Test backend for xmodule.modulestore app."""
from mock import Mock


def get_modulestore():
    """Test backend for eox_nelp.edxapp_wrapper.backends.modulestore_m_v1.

    Returns:
        Mock class.
    """
    return Mock()


def get_exception_ItemNotFoundError():
    """Test backend for eox_nelp.edxapp_wrapper.backends.modulestore_m_v1.

    Returns:
        Mock class.
    """
    return Exception
