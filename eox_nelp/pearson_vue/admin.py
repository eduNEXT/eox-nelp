"""
Admin configuration for the Pearson vue models.

This module defines the admin configuration for multiple models,
allowing administrators to view and manage instances of the model
in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from eox_nelp.pearson_vue.models import PearsonEngine, PearsonRTENEvent

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


class PearsonEngineAdmin(admin.ModelAdmin):
    """Admin class for PearsonEngineAdmin.

    attributes:
        list_display: Fields to be shown in admin interface.
        search_fields: fields that use to search and find matches.
    """
    @admin.display(ordering="user__username", description="User")
    def get_user_username(self, obj) -> str:
        """Return username from User instance"""
        return obj.user.username

    list_display = (
        "get_user_username",
        "rti_triggers",
        "cdd_triggers",
        "ead_triggers",
        "ead_courses",
        "rti_courses",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username",)
    raw_id_fields = ("user",)
    ordering = ("-updated_at",)
    readonly_fields = (
        "rti_triggers",
        "cdd_triggers",
        "ead_triggers",
        "ead_courses",
        "rti_courses",
    )


admin.site.register(PearsonRTENEvent, PearsonRTENEventAdmin)
admin.site.register(PearsonEngine, PearsonEngineAdmin)
