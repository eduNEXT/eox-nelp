"""Translation module to manage helpers related translations and languages."""
from crum import get_current_request
from django.conf import settings


def nelp_gettext(message):
    """Method that allow looking in settings with key `custom_translation` a possible translated message.
    If not the original django gettext method is used.

    Args:
        message (string): English message input to view to override the translation.

    Returns:
        string: Translation in the desired language.
    """
    # pylint: disable=import-outside-toplevel, unused-import

    translated_message = get_custom_translated_message(message)
    if translated_message:
        return translated_message

    from django.utils.translation import gettext_original
    return gettext_original(message)


def get_custom_translated_message(message):
    """Get custom translation of a message using  request,
    language_cookie_name, and the custom_translation dict setting.

    Args:
        message (string): string to search in settings custom translated msg.

    Returns:
        (str or None): If there is a possible translation return the string, if not return None.
    """
    request = get_current_request()
    if not request:
        return None
    custom_translations = getattr(settings, "custom_translations", {})
    if not custom_translations:
        return None
    user_language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if not user_language:
        return None

    return custom_translations.get(user_language, {}).get(message)
