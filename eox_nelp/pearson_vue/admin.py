"""
"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from eox_nelp.pearson_vue.models import PearsonRTENModel

User = get_user_model()


class PearsonRTENModelAdmin(admin.ModelAdmin):
    """Base class that allow to extract username from author field.

    methods:
        get_author_username: Returns username from User instance.
    """
    list_display = ("event_type", "created_at")
    readonly_fields = ("created_at",)


admin.site.register(PearsonRTENModel, PearsonRTENModelAdmin)
