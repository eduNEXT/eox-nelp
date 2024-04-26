"""Translation module to manage helpers related translations and languages."""
from crum import get_current_request
from django.conf import settings


def nelp_gettext(message):
    """_summary_

    Args:
        message (string): English message input to view to override the translation.

    Returns:
        string: Translation in the desired language.
    """
    # pylint: disable=import-outside-toplevel, unused-import
    if request := get_current_request():
        custom_translations = getattr(settings, "custom_translations", {})
        user_language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if custom_translations and user_language:
            if custom_translation := custom_translations.get(user_language).get(message):
                return custom_translation

    from django.utils.translation import gettext_original
    return gettext_original(message)
