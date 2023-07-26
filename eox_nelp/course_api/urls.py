"""eox_nelp course_api  urls
"""
from django.urls import include, path

app_name = 'eox_nelp'  # pylint: disable=invalid-name

urlpatterns = [
    path('payment-notifications/', NelpCourseListView.as_view(), name="payment-notifications"),
]
