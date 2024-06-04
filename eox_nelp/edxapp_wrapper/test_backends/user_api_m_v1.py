"""Backend test abstraction."""
from mock import Mock

from eox_nelp.tests.utils import set_key_values


def get_accounts():
    """Return test class.
    Returns:
        Mock class.
    """
    return Mock()


def get_errors():
    """Return test class.
    Returns:
        Mock class.
    """
    class AccountValidationError(Exception):
        def __init__(self, field_errors):  # pylint: disable=super-init-not-called
            self.field_errors = field_errors

    class AccountUpdateError(Exception):
        def __init__(self, developer_message, user_message):  # pylint: disable=super-init-not-called
            self.developer_message = developer_message
            self.user_message = user_message

    return set_key_values({
        "AccountValidationError": AccountValidationError,
        "AccountUpdateError": AccountUpdateError,
    })
