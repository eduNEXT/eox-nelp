"""
Payment Notifications views
"""


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from eox_nelp.payment_notifications.models import PaymentNotification
from eox_nelp.templates_config import render_to_response


@method_decorator(login_required, name='dispatch')
class PaymentNotificationsView(View):
    """
    Display a PaymentNotification for users that navigate to /payment-notifications
    """

    def get(self, request, *args, **kwargs):

        if not getattr(settings, "ENABLE_PAYMENT_NOTIFICATIONS", None):
            raise Http404


        return render_to_response("payment_notifications_with_frame.html", {})



def get_payment_notifications_context(request):
    """
    Calculate the notifications for a user.
    """
    default_context = {
        "payment_notifications": [],
    }

    if not getattr(settings, "ENABLE_PAYMENT_NOTIFICATIONS", None):
        return default_context

    user_id = request.user.id

    # allows staff users to masquerade to debug issues
    if request.GET.get("showpaymentnotificationsforuser", False) and request.user.is_staff:
        user_id = request.GET.get("showpaymentnotificationsforuser", user_id)

    all_notifications_for_user = PaymentNotification.objects.filter(cdtrans_lms_user_id=user_id)

    context = {
        "payment_notifications": all_notifications_for_user,
    }
    return context
