"""
Backend for courseware module.
"""

from lms.djangoapps.courseware import rules  # pylint: disable=import-error


def get_courseware_rules():
    """ get rules. """
    return rules
