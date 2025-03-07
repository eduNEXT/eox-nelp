"""eox_nelp user_profile api urls"""
from django.urls import include, path

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path("v1/", include("eox_nelp.user_profile.api.v1.urls", namespace="v1"))
]
