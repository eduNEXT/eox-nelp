"""
Settings for eox-core
"""
from __future__ import absolute_import, unicode_literals

SECRET_KEY = 'a-not-to-be-trusted-secret-key'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'social_django',
    'eox_nelp',
]

COURSE_CREATOR_APP = 'cms.djangoapps.course_creators'


def plugin_settings(settings):
    """
    Defines eox-nelp settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_NELP_COURSE_CREATORS_BACKEND = 'eox_nelp.edxapp_wrapper.backends.course_creators_k_v1'
    settings.EOX_NELP_COURSE_OVERVIEWS_BACKEND = 'eox_nelp.edxapp_wrapper.backends.course_overviews_m_v1'
    settings.EOX_NELP_SITE_CONFIGURATION = 'eox_nelp.edxapp_wrapper.backends.site_configuration_m_v1'
    settings.EOX_NELP_USER_API = 'eox_nelp.edxapp_wrapper.backends.user_api_m_v1'
    settings.EOX_NELP_USER_AUTHN = 'eox_nelp.edxapp_wrapper.backends.user_authn_m_v1'
    settings.EOX_NELP_MFE_CONFIG_VIEW = 'eox_nelp.edxapp_wrapper.backends.mfe_config_view_m_v1'
    settings.EOX_NELP_COURSE_API = 'eox_nelp.edxapp_wrapper.backends.course_api_m_v1'
    settings.EOX_NELP_XMODULE_MODULESTORE = 'eox_nelp.edxapp_wrapper.backends.modulestore_m_v1'
    settings.EOX_NELP_BULK_EMAIL_BACKEND = 'eox_nelp.edxapp_wrapper.backends.bulk_email_m_v1'
    settings.EOX_NELP_STUDENT_BACKEND = 'eox_nelp.edxapp_wrapper.backends.student_m_v1'

    settings.FUTUREX_API_URL = 'https://testing-site.com'
    settings.FUTUREX_API_CLIENT_ID = 'my-test-client-id'
    settings.FUTUREX_API_CLIENT_SECRET = 'my-test-client-secret'
    settings.BULK_EMAIL_DEFAULT_RETRY_DELAY = 30
    settings.BULK_EMAIL_MAX_RETRIES = 3

    if COURSE_CREATOR_APP not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append(COURSE_CREATOR_APP)
