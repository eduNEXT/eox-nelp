"""
Backend for instructor module.
"""

from lms.djangoapps.instructor import permissions  # pylint: disable=import-error


def get_instructor_permissions():
    """ get permissions. """
    return permissions
