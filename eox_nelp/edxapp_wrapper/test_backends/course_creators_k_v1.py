"""Test backend for course creators in admin module."""
from eox_nelp.edxapp_wrapper.test_backends import DummyAdmin, create_test_model


def get_course_creator_model():
    """Return test model.
    Returns:
        CourseCreator dummy model.
    """
    return create_test_model('CourseCreator', 'eox_nelp', __package__)


def get_course_creator_admin():
    """Return test class.
    Returns:
        Mock class.
    """
    return DummyAdmin
