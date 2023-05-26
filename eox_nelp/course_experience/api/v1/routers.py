"""Routes configuration for course experience views."""
from rest_framework import routers

from eox_nelp.course_experience.api.v1 import views

router = routers.DefaultRouter()
router.register("like/units", views.LikeDislikeUnitExperienceView, basename='like-units')
router.register("report/units", views.ReportUnitExperienceView, basename='report-units')
router.register("like/courses", views.LikeDislikeCourseExperienceView, basename='like-courses')
router.register("report/courses", views.ReportCourseExperienceView, basename='report-courses')
router.register("feedback/courses", views.FeedbackCourseExperienceView, basename='feedback-courses')
