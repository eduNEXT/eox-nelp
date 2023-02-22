"""
Settings for eox-nelp
"""

from .common import *  # pylint: disable=wildcard-import, unused-wildcard-import  # noqa: F401


class SettingsClass:
    """ dummy settings class """


def plugin_settings(settings):  # pylint: disable=function-redefined
    """
    Defines eox-nelp settings when app is used as a plugin to edx-platform.
    See: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.EOX_NELP_COURSE_CREATORS_BACKEND = 'eox_nelp.edxapp_wrapper.test_backends.course_creators_k_v1'
    settings.EOX_NELP_SITE_CONFIGURATION = 'eox_nelp.edxapp_wrapper.test_backends.site_configuration_m_v1'
    settings.EOX_NELP_USER_API = 'eox_nelp.edxapp_wrapper.test_backends.user_api_m_v1'
    settings.EOX_NELP_USER_AUTHN = 'eox_nelp.edxapp_wrapper.test_backends.user_authn_m_v1'
    settings.EOX_NELP_MFE_CONFIG_VIEW = 'eox_nelp.edxapp_wrapper.test_backends.mfe_config_view_m_v1'
    settings.EOX_NELP_COURSE_API = 'eox_nelp.edxapp_wrapper.test_backends.course_api_m_v1'


SETTINGS = SettingsClass()
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)


ALLOWED_HOSTS = ['*']

# This key needs to be defined so that the check_apps_ready passes and the
# AppRegistry is loaded
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

ENV_ROOT = '.'

FEATURES = {}
FEATURES['USE_REDIRECTION_MIDDLEWARE'] = True

COURSE_KEY_PATTERN = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
COURSE_ID_PATTERN = COURSE_KEY_PATTERN.replace('course_key_string', 'course_id')

USERNAME_REGEX_PARTIAL = r'[\w .@_+-]+'
USERNAME_PATTERN = fr'(?P<username>{USERNAME_REGEX_PARTIAL})'

PROCTORING_SETTINGS = {
    'LINK_URLS': {
        'contact_us': 'http://test-link.com/contact',
        'faq': 'http://test-link.com/faq',
        'online_proctoring_rules': 'http://test-link.com/rules',
        'tech_requirements': 'http://test-link.com/tech',
    },
    'SITE_NAME': 'test-site-name',
    'PLATFORM_NAME': 'test-platform-name',
}

PROCTORING_BACKENDS = {
    'software_secure': {
        'crypto_key': 'test-key',
        'exam_register_endpoint': 'test-enpoint',
        'exam_sponsor': 'test-sponsor',
        'organization': 'test-org',
        'secret_key': 'test-secret-key',
        'secret_key_id': 'test-secret-key-id',
        'software_download_url': 'http://test.com/url',
    },
    'DEFAULT': 'software_secure',
}
