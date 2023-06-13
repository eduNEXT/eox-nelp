"""Procedures urls file"""
from django.conf.urls import include
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import re_path

from eox_nelp.course_experience.frontend  import views
app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    re_path(r'^$', views.StartTemplate.as_view())
]
