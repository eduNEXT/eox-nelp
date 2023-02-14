"""eox_nelp mfe_config_api v1 urls
"""
from django.urls import path

from eox_nelp.mfe_config_api.v1 import views

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path('', views.NelpMFEConfigView.as_view(), name='nelp_mfe_config'),
]
