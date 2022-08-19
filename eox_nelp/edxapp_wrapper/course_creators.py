"""Wrapper course_creator module file.
This contains all the required dependencies from course_creators.
Attributes:
    backend:Imported ccx module by using the plugin settings.
    CourseCreator: Wrapper courseCreator model.
    CourseCreatorAdmin: Wrapper CourseCreatorAdmin class.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_COURSE_CREATORS_BACKEND)

CourseCreator = backend.get_course_creator_model()
CourseCreatorAdmin = backend.get_course_creator_admin()
