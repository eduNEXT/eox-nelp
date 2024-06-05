"""eox_nelp one_time_password api urls"""
from django.urls import include, path

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("v1/", include("eox_nelp.one_time_password.api.v1.urls", namespace="v1"))
]
