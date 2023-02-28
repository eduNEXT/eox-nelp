"""Test backend for course overviews module."""
from eox_nelp.edxapp_wrapper.test_backends import create_test_model


def get_course_overview_model():
    """Return test model.

    Returns:
        CourseOverview dummy model.
    """
    return create_test_model('CourseOverview', 'eox_nelp', __package__)
