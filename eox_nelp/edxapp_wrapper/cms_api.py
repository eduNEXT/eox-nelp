"""Wrapper of  cms api.

This contains  imports of modules from djangoapp cms/api/

Attributes:
    cms_api: Imported CMS api module by using the plugin settings.
    CourseRunViewSet: Wrapper cms course_run  api view class.
"""
from importlib import import_module

from django.conf import settings

cms_api = import_module(settings.EOX_NELP_CMS_API_BACKEND)

CourseRunViewSet = cms_api.get_course_runs_view()
