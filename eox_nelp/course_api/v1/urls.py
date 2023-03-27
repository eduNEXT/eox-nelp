"""
Course API URLs
"""
from django.conf import settings
from django.urls import path, re_path

from .views import NelpCourseDetailView, NelpCourseListView

app_name = "eox_nelp"  # pylint: disable=invalid-name
urlpatterns = [
    path('courses/', NelpCourseListView.as_view(), name="list"),
    re_path(rf'^courses/{settings.COURSE_KEY_PATTERN}', NelpCourseDetailView.as_view(), name="detail"),
]
