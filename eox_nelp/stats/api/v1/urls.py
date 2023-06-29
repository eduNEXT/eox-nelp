"""
Course API URLs
"""
from django.conf import settings
from django.urls import path, re_path

from eox_nelp.stats.api.v1.views import GeneralCourseStatsView, GeneralTenantStatsView

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path('tenant/', GeneralTenantStatsView.as_view(), name="general-stats"),
    path('courses/', GeneralCourseStatsView.as_view(), name="courses-stats"),
    re_path(rf'^courses/{settings.COURSE_ID_PATTERN}', GeneralCourseStatsView.as_view(), name="course-stats"),
]
