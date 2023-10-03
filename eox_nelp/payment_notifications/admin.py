"""
Payment notifications admin file.

This module contains the admin configuration for the PaymentNotification model.
It defines the admin class PaymentNotificationAdmin, which specifies how the
PaymentNotification model is displayed and interacted with in the Django admin interface.

Attributes:
    PaymentNotificationAdmin (admin.ModelAdmin): The admin class for PaymentNotification
        that customizes the display and functionality of the admin interface for this model.

This admin class defines the list of fields to be displayed, search fields, and filters
for PaymentNotification objects. It also includes several methods for summarizing
user data, transaction data, and message cases, which are used for displaying information
in the admin interface.

Methods:
    - user_summary(self, obj): Summarizes user data.
    - transaction_summary(self, obj): Summarizes transaction data.
    - msg_cases(self, obj): Shows message case state.
    - redirections_state(self, obj): Shows redirections state.
"""
from django.contrib import admin

from eox_nelp.payment_notifications.models import PaymentNotification


class PaymentNotificationAdmin(admin.ModelAdmin):
    """Admin class for PaymentNotification."""

    list_display = (
        "user_summary",
        "internal_status",
        "cdtrans_amount",
        "cdtrans_date",
        "transaction_summary",
        "msg_cases",
        "redirections_state",
        "internal_view_count",
    )
    search_fields = (
        "cdtrans_lms_user_id",
        "cdtrans_username",
        "cdtrans_email",
        "cdtrans_course_id",
        "cdtrans_response_id",
        "cdtrans_amount",
        "cdtrans_course_id",
        "internal_status",
        "cdtrans_cert_status",
        "cdtrans_enrollment_id",
        "cdtrans_sku",
    )
    list_filter = (
        "cdtrans_course_id",
        "cdtrans_amount",
        "internal_status",
        "show_msg_case0",
        "show_msg_case1",
        "show_msg_case2",
        "show_msg_custom",
        "redirect_from_dashboard",
        "redirect_from_course",
        "redirect_from_certificate",
        "redirect_from_everywhere",
    )

    def user_summary(self, obj):
        """Summaries user data"""
        return f"""
            lms_user_id: {obj.cdtrans_lms_user_id}
            username: {obj.cdtrans_username}
            email: {obj.cdtrans_email}
            course_id: {obj.cdtrans_course_id}
            enrollment_id: {obj.cdtrans_enrollment_id}
            certificate_status: {obj.cdtrans_cert_status}
        """

    def transaction_summary(self, obj):
        """Summaries transaction data"""
        return f"""
            sku: {obj.cdtrans_sku}
            response_id: {obj.cdtrans_response_id}
            status: {obj.cdtrans_status}
            response_ id: {obj.cdtrans_response_id}
            amount: {obj.cdtrans_amount}
            date: {obj.cdtrans_date}
        """

    def msg_cases(self, obj):
        """Show msg case state"""
        return f"""
            show_msg_case0: {obj.show_msg_case0}
            show_msg_case1: {obj.show_msg_case1}
            show_msg_case2: {obj.show_msg_case2}
        """

    def redirections_state(self, obj):
        """Show redirections state"""
        return f"""
            redirect_from_dashboard: {obj.redirect_from_dashboard}
            redirect_from_course: {obj.redirect_from_course}
            redirect_from_certificate: {obj.redirect_from_certificate}
            redirect_from_everywhere : {obj.redirect_from_everywhere}
        """


admin.site.register(PaymentNotification, PaymentNotificationAdmin)
