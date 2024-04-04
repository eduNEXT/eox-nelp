"""Client module for SMS vendor.

Classes:
    SMSVendorApiClient: Class to interact with SMS vendor  external service.
"""
from django.conf import settings

from eox_nelp.api_clients import AbstractNotAuthenticatedApiClient

try:
    from eox_audit_model.decorators import audit_method
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x


class SMSVendorApiClient(AbstractNotAuthenticatedApiClient):
    """Allow to perform SMS send operations."""

    @property
    def base_url(self):
        return getattr(settings, "SMS_VENDOR_URL")

    def send_sms(self, recipient, message):
        """This send SMS using an external Vendor via API.

        Arguments:
            recipient<str>: phone number, destination of message.
            message<str>: message body to be sent

        Returns:
            response<Dict>: requests response as dictionary.
        """
        @audit_method(action="Send SMS with sms_vendor API")
        def send_sms_request(recipient, message):
            """This is a wrapper that allows to make audit-able the send_SMS method."""
            path = getattr(settings, "SMS_VENDOR_SEND_SMS_PATH", "")
            payload = {
                "message": message,
                "number": recipient,
                "username": getattr(settings, "SMS_VENDOR_USERNAME"),
                "password": getattr(settings, "SMS_VENDOR_PASSWORD"),
                "sender": getattr(settings, "SMS_VENDOR_MSG_SENDER", "NELC"),
            }
            return self.make_post(path, payload)

        return send_sms_request(recipient, message)
