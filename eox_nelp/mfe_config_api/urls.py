"""eox_nelp mfe_config_api  urls
"""
from django.urls import include, path

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path('v1/', include('eox_nelp.mfe_config_api.v1.urls', namespace='mfe-config-api-v1')),
]
