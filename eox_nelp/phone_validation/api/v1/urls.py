"""eox_nelp phone_validation.api v1 urls"""
from django.urls import path

from eox_nelp.phone_validation.api.v1.views import generate_otp, validate_otp

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path('generate-otp/', generate_otp, name="generate-otp"),
    path('validate-otp/', validate_otp, name="validate-otp"),
]
