from crum import get_current_request
from django.conf import settings


def nelp_gettext(message):
    request = get_current_request()
    if request:
        if not hasattr(request, "tenant_config_custom_translations"):
            custom_translations = getattr(settings, "custom_translations", {})
            setattr(request, "tenant_config_custom_translations", custom_translations)

        custom_translation = request.tenant_config_custom_translations.get(
            request.COOKIES[settings.LANGUAGE_COOKIE_NAME], {}
        ).get(message, None)
        if custom_translation:
            return custom_translation

    from django.utils.translation import gettext_original

    return gettext_original(message)
