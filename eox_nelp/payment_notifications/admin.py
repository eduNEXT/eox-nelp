from django.contrib import admin

from eox_nelp.payment_notifications.models import PaymentNotification


class PaymentNotificationAdmin(admin.ModelAdmin):
    """Admin class for PaymentNotification."""

    list_display = (
        "cdtrans_lms_user_id",
        "cdtrans_username",
        "cdtrans_email",
        "cdtrans_course_id",
        "cdtrans_response_id",
        "cdtrans_amount",
    )
    search_fields = (
        "cdtrans_lms_user_id",
        "cdtrans_username",
        "cdtrans_email",
        "cdtrans_course_id",
        "cdtrans_response_id",
        "cdtrans_amount",
    )
    list_filter = (
        "cdtrans_lms_user_id",
        "cdtrans_username",
        "cdtrans_email",
        "cdtrans_course_id",
        "cdtrans_response_id",
        "cdtrans_amount",
    )


admin.site.register(PaymentNotification, PaymentNotificationAdmin)
