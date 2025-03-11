
"""eox_nelp external_certificates_manager.api v1 urls"""
from django.urls import path

from eox_nelp.external_certificates.api.v1.views import upsert_external_certificate

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [
    path("upsert/", upsert_external_certificate, name="upsert-external-certificate"),
]
