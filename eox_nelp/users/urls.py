"""
Main URLs for users.
"""
from django.urls import include, path

app_name = 'eox_nelp'  # pylint: disable=invalid-name
urlpatterns = [
    path('v1/', include('eox_nelp.users.api.v1.urls', namespace='v1')),
]
