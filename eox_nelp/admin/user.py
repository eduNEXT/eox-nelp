from django.contrib.auth import get_user_model
from eox_support.admin.user import SupportUserAdmin

from eox_nelp.admin.register_admin_model import register_admin_model as register

User = get_user_model()


class NelpUserAdmin(SupportUserAdmin):
    """EoxNelp User admin class."""

    list_display = ('user_national_id',) + SupportUserAdmin.list_display
    search_fields = SupportUserAdmin.search_fields + ('extrainfo__national_id',)
    fieldsets = SupportUserAdmin.fieldsets + (
        ('Extra info Fields', {'fields': ('user_national_id',)}),
    )
    readonly_fields = SupportUserAdmin.readonly_fields + ('user_national_id',)
    def user_national_id(self, instance):
        """Return national_id associated with the user extra_info instance."""
        if getattr(instance, "extrainfo", None):
            return instance.extrainfo.national_id

        return None


register(User, NelpUserAdmin)
