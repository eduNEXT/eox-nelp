"""Middleware file.

Required NELP middlewares that allow to customize edx-platform.

classes:
    ExtendedProfileFieldsMiddleware: Set extended_profile_fields in registration form.
    PreserveUserLanguageCookieMiddleware: Set the LANGUAGE cookie name with the original cookie sent by user.
"""
from django.conf import settings
from django.http import parse_cookie


class PreserveUserLanguageCookieMiddleware:
    """This middleware ensure that in the COOKIES property the LANGUAGE_COOKIE_NAME
    key has to be the cookie sent by the user and not other,
    because it could be modified previously by other.
    eg.
    https://github.com/openedx/edx-platform/blob/open-release/palm.master/openedx/
    core/djangoapps/lang_pref/middleware.py#L61-L62
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Process the request to change the language cookie based in original cookie value."""
        original_user_language_cookie = parse_cookie(request.META.get("HTTP_COOKIE", "")).get(
            settings.LANGUAGE_COOKIE_NAME
        )

        if original_user_language_cookie:
            request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = original_user_language_cookie

        return self.get_response(request)
