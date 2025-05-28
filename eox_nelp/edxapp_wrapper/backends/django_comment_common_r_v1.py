"""Backend for django_comment_common app.

This file contains all the necessary dependencies from
https://github.com/nelc/edx-platform/tree/open-release/redwood.nelp/openedx/core/djangoapps/django_comment_common
"""
from openedx.core.djangoapps.django_comment_common import comment_client  # pylint: disable=import-error


def get_comment_client():
    """Allow to get the package comment_client from
    https://github.com/nelc/edx-platform/tree/open-release/redwood.nelp/openedx/core/djangoapps/django_comment_common/comment_client

    Returns:
        comment_client package.
    """
    return comment_client
