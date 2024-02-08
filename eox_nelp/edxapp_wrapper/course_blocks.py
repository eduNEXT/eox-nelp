"""Wrapper for module in course_blocks app.
This contains all the required dependencies from course_blocks.
Attributes:
    get_student_module_as_dict: Wrapper get_student_module_as_dict function.
"""
from importlib import import_module

from django.conf import settings

backend = import_module(settings.EOX_NELP_COURSE_BLOCKS_BACKEND)

get_student_module_as_dict = backend.get_student_module_as_dict_method()
