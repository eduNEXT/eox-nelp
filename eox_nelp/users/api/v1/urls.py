"""
Users API v1 URLs.
"""
from django.urls import path

from .views import NelpEdxappUser

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [
    path('user/', NelpEdxappUser.as_view(), name='edxapp-user'),
]
