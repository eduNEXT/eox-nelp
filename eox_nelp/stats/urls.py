"""General stats urls"""
from django.urls import path

from eox_nelp.stats.views import get_tenant_stats

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path('tenant/', get_tenant_stats, name='tenant')
]
