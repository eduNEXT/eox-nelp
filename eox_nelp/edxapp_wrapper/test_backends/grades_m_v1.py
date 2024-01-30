"""Backend test abstraction."""
from mock import Mock


def get_course_grade_factory():
    """Test backend for eox_core.edxapp_wrapper.backends.grades_h_v1.

    Returns:
        Mock class.
    """
    return Mock()


def get_subsection_grade_factory():
    """Test backend for eox_nelp.edxapp_wrapper.backends.grades_m_v1.

    Returns:
        Mock class.
    """
    return Mock()
