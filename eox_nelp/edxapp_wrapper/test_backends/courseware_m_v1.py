"""Backend test abstraction."""
from mock import Mock


def get_courseware_courses():
    """Test backend for eox_core.edxapp_wrapper.backends.courseware_h_v1.

    Returns:
        Mock class.
    """
    return Mock


def get_courseware_rules():
    """Test backend for eox_nelp.edxapp_wrapper.backends.courseware_m_v1.

    Returns:
        Mock class.
    """
    return Mock()
