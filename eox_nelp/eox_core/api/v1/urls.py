"""
URLs for the API v1.
"""
from django.urls import re_path

from eox_nelp.eox_core.api.v1 import views

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [
    re_path(r'^user/$', views.NelpEdxappUser.as_view(), name='edxapp-user'),
]
