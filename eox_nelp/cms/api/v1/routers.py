"""Routes configuration for cms api views."""
from rest_framework import routers

from .views import NelpCourseRunViewSet

router = routers.DefaultRouter()
router.register(r'course_runs', NelpCourseRunViewSet, basename='course_run')
