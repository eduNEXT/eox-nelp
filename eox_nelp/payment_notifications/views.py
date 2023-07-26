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

        payment_notifications = PaymentNotification.objects.filter(cdtrans_lms_user_id=request.user.id)
        transaction_messages = [self.generate_payment_message(payment_notification) for payment_notification in payment_notifications]

        if not payment_notifications:
            message = "you don't have conflict payments"
        else:
            message = f"We found the following issues with your payments:"

        context = {
            "title": "Welcome to my great page",
            "general_message": message,
            "transaction_messages": transaction_messages,
            "payment_links": [
                "something",
                "something",
                "something",
            ]
        }
        return render_to_response("payment_notifications.html", context)

    def generate_payment_message(self, payment_notification):
        """Generate the message based on the PaymentNotification instance."""
        msgs = []

        ## temporal block
        msg_case0 = "This is the great msg case 0"
        msg_case1 = "This is the great msg case 1"
        msg_case2 = "This is the great msg case 2"

        if payment_notification.show_msg_case0:
            msgs.append(msg_case0)

        if payment_notification.show_msg_case1:
            msgs.append(msg_case1)

        if payment_notification.show_msg_case2:
            msgs.append(msg_case2)

        return f"""
            The transaction with id {payment_notification.cdtrans_response_id} performed the date {payment_notification.cdtrans_date}
            has the following errors: {" ".join(msgs)}
        """
