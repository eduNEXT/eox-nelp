"""
Payment Notifications views
"""


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings

from eox_nelp.payment_notifications.models import PaymentNotification



class PaymentNotificationsView(View):
    """
    Display a PaymentNotification for users that navigate to /payment-notifications
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, World!")
