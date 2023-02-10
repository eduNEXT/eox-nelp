"""
Course API URLs
"""
from django.conf import settings
from django.urls import path, re_path

from .views import NelpCourseDetailView, NelpCourseListView

urlpatterns = [
    path('v1/courses/', NelpCourseListView.as_view(), name="nelp-course-list"),
    re_path(rf'^v1/courses/{settings.COURSE_KEY_PATTERN}', NelpCourseDetailView.as_view(), name="nelp-course-detail"),
]
