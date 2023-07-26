from django.contrib import admin

from eox_nelp.payment_notifications.models import PaymentNotification


class PaymentNotificationAdmin(admin.ModelAdmin):
    """Admin class for PaymentNotification."""


admin.site.register(PaymentNotification, PaymentNotificationAdmin)
