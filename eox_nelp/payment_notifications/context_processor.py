"""
Get the payment notifications context.

This function is used to obtain the necessary context for payment notifications
and returns it as a dictionary.

Args:
    request: The HttpRequest object representing the HTTP request.

Returns:
    dict: A dictionary with the payment notifications context.
"""
from eox_nelp.payment_notifications.views import get_payment_notifications_context


def payments_notifications_context(request):
    """
    This function works as a payment notification context
    """
    return get_payment_notifications_context(request)
