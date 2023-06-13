"""frontend templates urls for course_experience"""
from django.urls import path

from eox_nelp.course_experience.frontend import views

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path('feedback/courses/', views.FeedbackCoursesTemplate.as_view(), name='feedback-courses')
]
