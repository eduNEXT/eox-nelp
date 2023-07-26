"""
eox_nelp notifications for payment status
"""
from django.urls import path

from eox_nelp.payment_notifications.views import PaymentNotificationsView

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("", PaymentNotificationsView.as_view(), name="payment-notifications"),
]
