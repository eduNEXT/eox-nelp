"""eox_nelp course_experience_api v1 urls
"""
from eox_nelp.course_experience.api.v1.routers import router

app_name = "eox_nelp"  # pylint: disable=invalid-name
urlpatterns = router.urls
