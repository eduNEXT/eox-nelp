"""Utils module to dont repeat code."""
import logging

from django.core.exceptions import MultipleObjectsReturned

logger = logging.getLogger(__name__)


def match_user_using_uid_query(backend, response, user_query):
    """Look up for a user using query to match uid.
    The uid is based in the configuration of the saml with the field `attr_user_permanent_id`:
    https://github.com/python-social-auth/social-core/blob/master/social_core/backends/saml.py#L49

    This is using the idp and the uid inspired in:
    https://github.com/python-social-auth/social-core/blob/master/social_core/backends/saml.py#L296C23-L297
    Args:
        backend (backend): backend to use strategy to get user model
        response (dict): Response Dict
        user_query (str): string query to find the user.
    Returns:
        user_match(User): User matched object or None
    """
    user_match = None
    idp = backend.get_idp(response["idp_name"])
    uid = idp.get_user_permanent_id(response["attributes"])
    try:
        user_match = backend.strategy.storage.user.get_user(**{user_query: uid})
    except MultipleObjectsReturned as exc:
        logger.info(
            "Pipeline tries to match user with uid(%s) using %s, but Multiple users found: %s",
            uid,
            user_query,
            str(exc),
        )

    return user_match
