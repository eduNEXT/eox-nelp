"""
Admin configuration for the Pearson vue models.

This module defines the admin configuration for multiple models,
allowing administrators to view and manage instances of the model
in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from eox_nelp.pearson_vue.models import PearsonRTENEvent

User = get_user_model()


class PearsonRTENEventAdmin(admin.ModelAdmin):
    """
    Admin class for the PearsonRTENEvent model.

    Attributes:
        list_display (list): List of fields to display in the admin list view.
        readonly_fields (tuple): Tuple of fields that are read-only in the admin interface.
    """
    list_display = ("event_type", "candidate", "course", "created_at")
    readonly_fields = ("created_at", "candidate", "course", "event_type")
    list_filter = ["event_type"]


admin.site.register(PearsonRTENEvent, PearsonRTENEventAdmin)
