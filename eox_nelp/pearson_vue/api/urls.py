"""
Top-level URL configuration for the pearson vue api..

This module defines the URL patterns for the pearson vue api..
"""
from django.urls import include, path

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path('v1/', include('eox_nelp.pearson_vue.api.v1.urls', namespace='v1')),
]
