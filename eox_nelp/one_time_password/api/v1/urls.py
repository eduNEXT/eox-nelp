"""eox_nelp one_time_password api v1 urls"""
from django.urls import path

from eox_nelp.one_time_password.api.v1.views import generate_otp, validate

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path("generate/", generate_otp, name="generate-otp"),
    path("validate/", validate, name="validate-otp"),
]
