"""
eox_nelp model for notifications
"""
import json
import logging

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class PaymentNotification(models.Model):
    """
    PaymentNotification model
    """
    id = models.AutoField(primary_key=True)

    # This data comes from the Payment transaction
    cdtrans_lms_user_id = models.IntegerField(db_index=True, null=True, blank=True)

    cdtrans_sku = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_username = models.CharField(max_length=200, null=True, blank=True)
    cdtrans_email = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_amount = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_course_id = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_enrollment_id = models.IntegerField(null=True, blank=True)
    cdtrans_mode = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_cert_status = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_date = models.DateTimeField(null=True, blank=True)
    cdtrans_response_id = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_status = models.CharField(max_length=100, null=True, blank=True)
    cdtrans_ecom_order_id = models.IntegerField(null=True, blank=True)
    cdtrans_ecom_payment_reponse_id = models.IntegerField(null=True, blank=True)

    cdtrans_card_last_4_digits = models.CharField(max_length=10, null=True, blank=True)

    cdtrans_extra_data_1 = models.CharField(max_length=1000, null=True, blank=True)
    cdtrans_extra_data_2 = models.CharField(max_length=1000, null=True, blank=True)
    cdtrans_extra_data_3 = models.CharField(max_length=1000, null=True, blank=True)
    cdtrans_extra_data_4 = models.TextField(null=True, blank=True)

    # Control surface
    show_msg_case0 = models.BooleanField(null=True, blank=True, help_text="Not ready")
    show_msg_case1 = models.BooleanField(null=True, blank=True, help_text="Not ready")
    show_msg_case2 = models.BooleanField(null=True, blank=True, help_text="Not ready")

    show_trans_info = models.BooleanField(null=True, blank=True, help_text="Not ready")

    show_msg_custom = models.BooleanField(null=True, blank=True, help_text="Not ready")
    custom_msg = models.TextField(null=True, blank=True, help_text="Not ready")

    call_to_action_1_msg = models.CharField(max_length=1000, null=True, blank=True, help_text="Not ready")
    call_to_action_2_msg = models.CharField(max_length=1000, null=True, blank=True, help_text="Not ready")
    call_to_action_3_msg = models.CharField(max_length=1000, null=True, blank=True, help_text="Not ready")

    call_to_action_1_url = models.CharField(max_length=1000, null=True, blank=True, help_text="Not ready")
    call_to_action_2_url = models.CharField(max_length=1000, null=True, blank=True, help_text="Not ready")
    call_to_action_3_url = models.CharField(max_length=1000, null=True, blank=True, help_text="Not ready")

    redirect_from_dashboard = models.BooleanField(null=True, blank=True, help_text="Not ready")
    redirect_from_course = models.BooleanField(null=True, blank=True, help_text="Not ready")
    redirect_from_certificate = models.BooleanField(null=True, blank=True, help_text="Not ready")
    redirect_from_everywhere = models.BooleanField(null=True, blank=True, help_text="Not ready")

    # Dashboard control
    INTERNAL_STATUS = [
        ("case_0", "case_0"),
        ("case_1", "case_1"),
        ("case_2", "case_2"),
        ("pending_manual_eval", "pending_manual_eval"),
        ("other_case", "other_case"),
        ("ignore", "ignore"),
        ("resolution_by_case_0", "resolution_by_case_0"),
        ("resolution_by_case_1", "resolution_by_case_1"),
        ("resolution_by_case_2", "resolution_by_case_2"),
        ("resolution_other", "resolution_other"),
    ]
    internal_status = models.CharField(
        max_length=30,
        choices=INTERNAL_STATUS,
        default='case_0',
    )
    internal_notes = models.TextField(max_length=2000, null=True, blank=True)

    internal_view_count = models.IntegerField(default=0)
