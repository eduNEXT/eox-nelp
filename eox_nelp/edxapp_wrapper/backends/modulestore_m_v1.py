"""Backend for xmodule.modulestore app.

This file contains all the necessary dependencies from
https://github.com/eduNEXT/edunext-platform/blob/master/common/lib/xmodule/xmodule/modulestore
"""
from xmodule.modulestore.django import SignalHandler, modulestore  # pylint: disable=import-error


def get_modulestore():
    """Allow to get modulestore function from
    https://github.com/eduNEXT/edunext-platform/blob/master/common/lib/xmodule/xmodule/modulestore/django.py#L311

    Returns:
        modulestore function.
    """
    return modulestore


def get_course_published_signal():
    """Allow to get the course_published from
    https://github.com/eduNEXT/edunext-platform/blob/master/common/lib/xmodule/xmodule/modulestore/django.py#L167

    Returns:
        course_published SwitchedSignal.
    """
    return SignalHandler.course_published
