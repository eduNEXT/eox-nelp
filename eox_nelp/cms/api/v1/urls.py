"""eox_nelp cms_api v1 urls
"""
from eox_nelp.cms.api.v1.routers import router

app_name = "eox_nelp"  # pylint: disable=invalid-name
urlpatterns = router.urls
