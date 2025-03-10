"""
Admin module for the external_certificates.
"""
from django.contrib import admin

from eox_nelp.external_certificates.models import ExternalCertificate


@admin.register(ExternalCertificate)
class ExternalCertificateAdmin(admin.ModelAdmin):
    """
    Admin class for managing ExternalCertificate models.
    """
    list_display = ("certificate_id", "user", "group_code", "created_at")
    search_fields = ("certificate_id", "user__username")
    list_filter = ("created_at", "group_code")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {
            "fields": ("certificate_id", "user", "group_code")
        }),
        ("Certificate URLs", {
            "fields": ("certificate_url_en", "certificate_url_ar")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )
