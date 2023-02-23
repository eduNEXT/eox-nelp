"""Backend test abstraction."""
from mock import Mock

from eox_nelp.edxapp_wrapper.test_backends import DummyView


def get_course_detail_serializer():
    """Return test class.
    Returns:
        Mock class.
    """
    return Mock


def get_course_detail_view():
    """Return test class.
    Returns:
        Mock class.
    """
    return DummyView


def get_course_list_view():
    """Return test class.
    Returns:
        Mock class.
    """
    return DummyView
