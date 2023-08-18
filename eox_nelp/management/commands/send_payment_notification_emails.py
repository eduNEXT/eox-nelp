""""Management command to send email to payment notifications. If conditions are
satisfied, manage the delivery sending mass email.
To run it use:
`./manage lms send_payment_notification_emails`.
"""

import logging
from datetime import datetime
from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail, send_mass_mail
from django.core import mail
from eox_nelp.notifications.utils import send_email_multialternative
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from django.contrib.auth import get_user_model
from eox_nelp.payment_notifications.models import PaymentNotification

User = get_user_model()

logger = logging.getLogger(__name__)

CASE_1_EMAIL_SUBJECT = "[مهم] مشكلة في الدفع لدورة {course_name} في المعهد العقاري السعودي"

CASE_1_EMAIL_BODY = """
السلام عليكم،

إلى {learner_name} مع التحية،

هذه الرسالة بخصوص مشكلة في عميلة الدفع لتسجيلكم في دورة "{course_name}" في المعهد السعودي العقاري.

حصل خطأ في الدفعة التي جرت بتاريخ {payment_date} وقيمتها {invoice_total_amount} ريال سعودي ولم يتم استيفاء الرسوم المترتبة على الانضمام للدورة.

يرجى الدخول إلى حسابكم في المنصة التعليمية للمعهد وإعادة الدفع: https://srei.futurex.sa/dashboard

أو يمكنكم الدفع مباشرة بالذهاب لهذا الرابط: {payment_url}

إذا كنت متأكداً بأن عملية الدفع الخاصة بك قد تمت بنجاح، الرجاء مراسلتنا على البريد التالي مع إرفاق صورة عن إثبات الدفع مثل كشف الحساب من بطاقة الإتمان أو بطاقة مدى على الإيميل
{support_email}

مع فائق الشكر،

--

فريق المعهد العقاري السعودي على منصة FutureX.sa
"""
CASE_1_EMAIL_HTML_BODY = """
<div style="direction:rtl;">
<p>السلام عليكم،</p>
<p>إلى {learner_name} مع التحية،</p>
<p>هذه الرسالة بخصوص مشكلة في عميلة الدفع لتسجيلكم في دورة "{course_name}" في المعهد السعودي العقاري.</p>
<p>حصل خطأ في الدفعة التي جرت بتاريخ {payment_date} وقيمتها {invoice_total_amount} ريال سعودي ولم يتم استيفاء الرسوم المترتبة على الانضمام للدورة.</p>
<p>يرجى الدخول إلى حسابكم في المنصة التعليمية للمعهد وإعادة الدفع: https://srei.futurex.sa/dashboard</p>
<p>أو يمكنكم الدفع مباشرة بالذهاب لهذا الرابط: {payment_url}</p>
<p>إذا كنت متأكداً بأن عملية الدفع الخاصة بك قد تمت بنجاح، الرجاء مراسلتنا على البريد التالي مع إرفاق صورة عن إثبات الدفع مثل كشف الحساب من بطاقة الإتمان أو بطاقة مدى على الإيميل</p>
<p>{support_email}</p>
<p>مع فائق الشكر،</p>
<p>--</p>
<p>فريق المعهد العقاري السعودي على منصة FutureX.sa</p>
</div>
"""

class Command(BaseCommand):
    """Class command to send case 1 payment notifications."""
    def add_arguments(self, parser):
        parser.add_argument(
            '--payment_notifications_ids',
            nargs="+",
            type=int,
            required=False,
            help='Indicate specific payment notification to sent id'
        )
        parser.add_argument(
            '--bcc',
            nargs="+",
            required=False,
            help='Indicate secret bcc to send emails'
        )
    def handle(self, *args, **kwargs):  # lint-amnesty, pylint: disable=too-many-statements
        logger.info('----Processing payment notifications to send email-----')
        start_time = datetime.now()
        payment_notifications_ids = kwargs.get('payment_notifications_ids')
        bcc = kwargs.get('bcc')
        if payment_notifications_ids:
            delivery_qs = PaymentNotification.objects.filter(  # pylint: disable=no-member
                id__in=payment_notifications_ids,
            )
        else:
            delivery_qs = PaymentNotification.objects.filter(  # pylint: disable=no-member
                internal_status="case_1",
            )
        emails_list = []
        """_
            message1 = (
                "Subject here",
                "Here is the message",
                "from@example.com",
                ["first@example.com", "other@example.com"],
            )
        """
        correct_payment_notifications = []
        failed_payment_notifications = []
        mail_connection = mail.get_connection()
        mail_connection.open()
        for payment_notification in delivery_qs:
            try:
                email_multialternative_data = generate_email_multialternative_data(payment_notification)
                send_email_multialternative(**email_multialternative_data, connection=mail_connection, bcc=bcc)
                correct_payment_notifications.append(payment_notification.id)
            except Exception as e:
                logger.error("There was an error processing payment notification %s",payment_notification.id)
                logger.error(e)
                failed_payment_notifications.append(payment_notification.id)
        emails = tuple(emails_list)
        logger.info('----Start sendig mass email: approx %s-----', len(correct_payment_notifications))

        emails_sent = send_mass_mail(emails, fail_silently=False)
        logger.info('----Sending summary emails to managers-----')
        mail_connection.close()
        send_summary_email(correct_payment_notifications, failed_payment_notifications, emails_sent=emails_sent)
        end_time = datetime.now()
        script_runtime = end_time - start_time
        logger.info('----The command run with a time of approx %s-----', str(script_runtime))


def get_notification_data_from_payment_notification(payment_notification):
    """get data for each payment_notification
    """
    course_overview = CourseOverview.objects.get(id=payment_notification.cdtrans_course_id)
    user = User.objects.get(id=payment_notification.cdtrans_lms_user_id)
    extra_info = getattr(user, "extrainfo", None)
    if extra_info:
        learner_name = user.extrainfo.arabic_name
    elif user.first_name:
        learner_name = user.first_name + user.last_name
    else:
        learner_name = user.username
    return {
        "course_name": course_overview.display_name,
        "learner_name": learner_name,
        "payment_date": payment_notification.cdtrans_date.strftime("%d-%m-%Y"), #check format to manage this datetime
        "invoice_total_amount": payment_notification.cdtrans_amount,
        "payment_url": f"https://srei.ecommerce.futurex.sa/basket/add/?sku={payment_notification.cdtrans_sku}",
        "support_email": "srei.care@elc.edu.sa",
    }


def send_summary_email(correct, failed, emails_sent=None):
    """send refund summarry order email."""
    correct_total = len(correct)
    failed_total = len(failed)
    msg = f"""
    Emails sent: {emails_sent}
    Number correct_processed: {correct_total}
    Number failed_processed {failed_total}
    Correct payment notifications processed: {correct}
    Failed payment notifications processed: {failed}
    """
    send_mail(
        "Emails, correct summary",
        msg,
        None,
        ["johan.castiblanco@edunext.co", "andrey.canon@edunext.co"],
        fail_silently=False,
    )


def generate_email_multialternative_data(payment_notification):
    """generate dict data to sent email multialternative"""
    notification_data = get_notification_data_from_payment_notification(payment_notification)

    return {
        "subject": CASE_1_EMAIL_SUBJECT.format(**notification_data),
        "plaintext_msg": CASE_1_EMAIL_BODY.format(**notification_data),
        "html_msg": CASE_1_EMAIL_HTML_BODY.format(**notification_data),
        "recipient_emails": [payment_notification.cdtrans_email]

    }
