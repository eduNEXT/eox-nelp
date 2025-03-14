
"""eox_nelp external_certificates_manager.api v1 urls"""
from django.urls import path

from eox_nelp.external_certificates.api.v1.views import UpsertExternalCertificateView

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [
    path("upsert/", UpsertExternalCertificateView.as_view(), name="upsert-external-certificate"),
]
