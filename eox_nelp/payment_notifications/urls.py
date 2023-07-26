"""
eox_nelp notifications for payment status
"""
from django.urls import include, path

from eox_nelp.payment_notifications.views import PaymentNotificationsView

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("payment-notifications/", PaymentNotificationsView.as_view(), name="payment-notifications"),
]
