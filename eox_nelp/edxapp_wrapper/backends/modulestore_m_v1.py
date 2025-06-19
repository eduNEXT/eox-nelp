"""Backend for xmodule.modulestore app.

This file contains all the necessary dependencies from
https://github.com/eduNEXT/edunext-platform/blob/master/common/lib/xmodule/xmodule/modulestore
"""
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error
from xmodule.modulestore.exceptions import ItemNotFoundError


def get_modulestore():
    """Allow to get modulestore function from
    https://github.com/eduNEXT/edunext-platform/blob/master/common/lib/xmodule/xmodule/modulestore/django.py#L311

    Returns:
        modulestore function.
    """
    return modulestore


def get_exception_ItemNotFoundError():
    """Allow to get ItemNotFoundError Exception from
    https://github.com/eduNEXT/edunext-platform/blob/master/common/lib/xmodule/xmodule/modulestore/exceptions.py#L6

    Returns:
        ItemNotFoundError Exception.
    """
    return ItemNotFoundError
