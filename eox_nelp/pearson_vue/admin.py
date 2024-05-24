"""
Admin configuration for the Pearson vue models.

This module defines the admin configuration for multiple models,
allowing administrators to view and manage instances of the model
in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from eox_nelp.pearson_vue.models import PearsonRTENModel

User = get_user_model()


class PearsonRTENModelAdmin(admin.ModelAdmin):
    """
    Admin class for the PearsonRTENModel model.

    Attributes:
        list_display (list): List of fields to display in the admin list view.
        readonly_fields (tuple): Tuple of fields that are read-only in the admin interface.
    """
    list_display = ("event_type", "created_at")
    readonly_fields = ("created_at",)


admin.site.register(PearsonRTENModel, PearsonRTENModelAdmin)
