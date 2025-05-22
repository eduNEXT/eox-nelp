"""
Main URLs for eox-core.
"""
from django.urls import include, path

app_name = 'eox_nelp'

urlpatterns = [
    path('api/v1/', include('eox_nelp.eox_core.api.v1.urls', namespace='v1')),
]
