"""Wrapper grades djangoapp.
This contains all the required dependencies from grades.
Attributes:
    backend:Imported module by using the plugin settings.
    SubsectionGradeFactory: Wrapper for SubsectionGradeFactory class.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_GRADES_BACKEND)

SubsectionGradeFactory = backend.get_subsection_grade_factory()
