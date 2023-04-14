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
EOX_NELP_BEAT_SCHEDULES = {
    'log_message_task': {
        'task': 'eox_nelp.tasks.log_message',  # Update with your app's task path
        'schedule': 60.0,  # 300 seconds = 5 minutes
    },
}


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

    settings.FUTUREX_API_URL = 'https://testing-site.com'
    settings.FUTUREX_API_CLIENT_ID = 'my-test-client-id'
    settings.FUTUREX_API_CLIENT_SECRET = 'my-test-client-secret'

    if COURSE_CREATOR_APP not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append(COURSE_CREATOR_APP)

    if getattr(settings, 'CELERYBEAT_SCHEDULE', None):
        settings.CELERYBEAT_SCHEDULE = {**settings.CELERYBEAT_SCHEDULE, **EOX_NELP_BEAT_SCHEDULES}
    else:
        setattr(settings, 'CELERYBEAT_SCHEDULE', EOX_NELP_BEAT_SCHEDULES)
