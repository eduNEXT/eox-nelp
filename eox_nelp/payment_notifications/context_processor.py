"""
"""
from eox_nelp.payment_notifications.views import get_payment_notifications_context


def payments_notifications_context(request):
    """
    """
    return get_payment_notifications_context(request)
