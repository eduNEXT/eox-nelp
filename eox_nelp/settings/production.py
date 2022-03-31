"""
Settings for eox_nelp project meant to be called on the edx-platform/*/envs/aws.py module
"""
from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ImportError:
    sentry_sdk = DjangoIntegration = None


def plugin_settings(settings):  # pylint: disable=function-redefined
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """

    settings.eox_nelp_BEARER_AUTHENTICATION = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_BEARER_AUTHENTICATION',
        settings.eox_nelp_BEARER_AUTHENTICATION
    )







    settings.eox_nelp_THIRD_PARTY_AUTH_BACKEND = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_THIRD_PARTY_AUTH_BACKEND',
        settings.eox_nelp_THIRD_PARTY_AUTH_BACKEND
    )
    settings.eox_nelp_USER_ENABLE_MULTI_TENANCY = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_USER_ENABLE_MULTI_TENANCY',
        settings.eox_nelp_USER_ENABLE_MULTI_TENANCY
    )
    if not settings.eox_nelp_USER_ENABLE_MULTI_TENANCY:
        user_origin_sources = [
            'fetch_from_unfiltered_table',
        ]
    else:
        user_origin_sources = settings.eox_nelp_USER_ORIGIN_SITE_SOURCES
    settings.eox_nelp_USER_ORIGIN_SITE_SOURCES = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_USER_ORIGIN_SITE_SOURCES',
        user_origin_sources
    )

    settings.eox_nelp_APPEND_LMS_MIDDLEWARE_CLASSES = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_APPEND_LMS_MIDDLEWARE_CLASSES',
        settings.eox_nelp_APPEND_LMS_MIDDLEWARE_CLASSES
    )
    if settings.SERVICE_VARIANT == "lms":
        if settings.eox_nelp_APPEND_LMS_MIDDLEWARE_CLASSES:
            settings.MIDDLEWARE += [
                'eox_nelp.middleware.PathRedirectionMiddleware',
                'eox_nelp.middleware.RedirectionsMiddleware',
                'eox_nelp.middleware.TPAExceptionMiddleware'
            ]

    # Sentry Integration
    sentry_integration_dsn = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_SENTRY_INTEGRATION_DSN',
        settings.eox_nelp_SENTRY_INTEGRATION_DSN
    )
    settings.eox_nelp_SENTRY_IGNORED_ERRORS = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_SENTRY_IGNORED_ERRORS',
        settings.eox_nelp_SENTRY_IGNORED_ERRORS
    )
    sentry_environment = getattr(settings, 'ENV_TOKENS', {}).get(
        'eox_nelp_SENTRY_ENVIRONMENT',
        settings.eox_nelp_SENTRY_ENVIRONMENT
    )

    if sentry_sdk is not None and sentry_integration_dsn is not None:
        from eox_nelp.integrations.sentry import ExceptionFilterSentry  # pylint: disable=import-outside-toplevel
        sentry_sdk.init(
            before_send=ExceptionFilterSentry(),
            dsn=sentry_integration_dsn,
            environment=sentry_environment,
            integrations=[
                DjangoIntegration(),
            ],

            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True
        )
