"""
Wrapper xmodule.modulestore module.

This contains all the required dependencies from modulestore

Attributes:
    backend:Imported module by using the plugin settings.
    CourseCreator: Wrapper CourseCreator model.
    CourseCreatorAdmin: Wrapper CourseCreatorAdmin class.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_XMODULE_MODULESTORE)

modulestore = backend.get_modulestore()
course_published = backend.get_course_published_signal()
