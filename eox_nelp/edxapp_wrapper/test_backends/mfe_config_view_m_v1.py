"""Backend test abstraction."""
from eox_nelp.edxapp_wrapper.test_backends import DummyView


def get_MFE_config_view():
    """Return test class.
    Returns:
        Mock class.
    """
    return DummyView
