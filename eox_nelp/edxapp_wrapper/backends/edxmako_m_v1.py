""" Backend abstraction """
from common.djangoapps import edxmako  # pylint: disable=import-error


def get_edxmako():
    """Allow to get edxmako from
    https://github.com/eduNEXT/edx-platform/blob/open-release/maple.master/common/djangoapps/edxmako/__init__.py

    Returns:
        edxmako module.
    """
    return edxmako
