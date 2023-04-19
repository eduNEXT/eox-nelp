"""This file contains all the test for notifications/admin.py file.

Classes:
    NotifyDueDateTestCase: Test notify_due_dates function.
"""
import unittest

from mock import MagicMock

from eox_nelp.notifications.admin import notify_due_dates


class NotifyDueDateTestCase(unittest.TestCase):
    """Test class for function notify_due_dates"""

    def test_notify(self):
        """Test that the method 'notify' is called'.

        Expected behavior:
            - Notify is called.
        """
        mock_queryset = MagicMock()
        items = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        mock_queryset.__iter__.return_value = items

        notify_due_dates(None, None, mock_queryset)

        for item in items:
            item.notify.assert_called_once()
