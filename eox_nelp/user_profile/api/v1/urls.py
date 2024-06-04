"""eox_nelp puser_profile.api v1 urls"""
from django.urls import path

from eox_nelp.user_profile.api.v1.views import generate_otp, update_user_data

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path("generate-otp/", generate_otp, name="generate-otp"),
    path("update-user-data/", update_user_data, name="update-user-data"),
]
