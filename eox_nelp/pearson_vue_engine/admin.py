"""
Admin configuration for the Pearson vue models.

This module defines the admin configuration for multiple models,
allowing administrators to view and manage instances of the model
in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from eox_nelp.pearson_vue_engine.models import PearsonEngine

User = get_user_model()


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
        "courses",
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
        "courses",
    )


admin.site.register(PearsonEngine, PearsonEngineAdmin)
