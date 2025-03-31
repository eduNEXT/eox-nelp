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
    list_display = ("certificate_id", "user", "course_overview", "created_at")
    search_fields = ("certificate_id", "user__username")
    list_filter = ("created_at", "course_overview")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {
            "fields": ("certificate_id", "user", "course_overview")
        }),
        ("Certificate URLs", {
            "fields": ("certificate_url_en", "certificate_url_ar")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )
