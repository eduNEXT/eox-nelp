"""
This module defines the Django admin configuration for handling user model.

Classes:
    NelpUserAdmin: Custom admin class for User model to include extra info fields like national_id.
"""
from importlib import import_module
from importlib.util import find_spec

from custom_reg_form.models import ExtraInfo
from django.conf import settings
from django.contrib.admin import StackedInline
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from eox_nelp.admin.register_admin_model import register_admin_model as register

if find_spec('eox_support') and 'eox_support.apps.EoxSupportConfig' in settings.INSTALLED_APPS:
    SupportUserAdmin = import_module("eox_support.admin.user").SupportUserAdmin
else:
    SupportUserAdmin = BaseUserAdmin

User = get_user_model()

class UserExtraInfoInline(StackedInline):
    """ Inline admin interface for Extra Info model. """
    model = ExtraInfo
    can_delete = False
    verbose_name_plural = ('Extra info')


class NelpUserAdmin(SupportUserAdmin):
    """EoxNelp User admin class."""
    list_display = SupportUserAdmin.list_display[:2] + ('user_national_id',) + SupportUserAdmin.list_display[2:]
    search_fields = SupportUserAdmin.search_fields + ('extrainfo__national_id',)
    inlines = SupportUserAdmin.inlines + (UserExtraInfoInline,)
    readonly_fields = SupportUserAdmin.readonly_fields + ('user_national_id',)

    def user_national_id(self, instance):
        """Return national_id associated with the user extra_info instance."""
        if getattr(instance, "extrainfo", None):
            return instance.extrainfo.national_id

        return None


if find_spec('eox_support') and 'eox_support.apps.EoxSupportConfig' in settings.INSTALLED_APPS:
    register(User, NelpUserAdmin)
