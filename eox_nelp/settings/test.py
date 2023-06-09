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
    settings.EOX_NELP_COURSE_OVERVIEWS_BACKEND = 'eox_nelp.edxapp_wrapper.test_backends.course_overviews_m_v1'
    settings.EOX_NELP_SITE_CONFIGURATION = 'eox_nelp.edxapp_wrapper.test_backends.site_configuration_m_v1'
    settings.EOX_NELP_USER_API = 'eox_nelp.edxapp_wrapper.test_backends.user_api_m_v1'
    settings.EOX_NELP_USER_AUTHN = 'eox_nelp.edxapp_wrapper.test_backends.user_authn_m_v1'
    settings.EOX_NELP_MFE_CONFIG_VIEW = 'eox_nelp.edxapp_wrapper.test_backends.mfe_config_view_m_v1'
    settings.EOX_NELP_COURSE_API = 'eox_nelp.edxapp_wrapper.test_backends.course_api_m_v1'
    settings.EOX_NELP_XMODULE_MODULESTORE = 'eox_nelp.edxapp_wrapper.test_backends.modulestore_m_v1'
    settings.EOX_NELP_BULK_EMAIL_BACKEND = 'eox_nelp.edxapp_wrapper.test_backends.bulk_email_m_v1'
    settings.EOX_NELP_STUDENT_BACKEND = 'eox_nelp.edxapp_wrapper.test_backends.student_m_v1'

    settings.FUTUREX_API_URL = 'https://testing.com'
    settings.FUTUREX_API_CLIENT_ID = 'my-test-client-id'
    settings.FUTUREX_API_CLIENT_SECRET = 'my-test-client-secret'
    settings.FUTUREX_NOTIFY_SUBSECTION_SUBJECT_MESSAGE = DEFAULT_FUTUREX_NOTIFY_SUBSECTION_SUBJECT_MESSAGE  # noqa: F405


SETTINGS = SettingsClass()
plugin_settings(SETTINGS)
vars().update(SETTINGS.__dict__)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

ALLOWED_HOSTS = ['*']
ENV_ROOT = '.'
ROOT_URLCONF = 'eox_nelp.urls'

COURSE_KEY_PATTERN = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
COURSE_ID_PATTERN = COURSE_KEY_PATTERN.replace('course_key_string', 'course_id')

USERNAME_REGEX_PARTIAL = r'[\w .@_+-]+'
USERNAME_PATTERN = fr'(?P<username>{USERNAME_REGEX_PARTIAL})'

SILENCED_SYSTEM_CHECKS = [
    'admin.E403', 'admin.E406', 'admin.E408', 'admin.E409', 'admin.E410', 'admin.E002', 'admin.E035',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
TESTING_MIGRATIONS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'edx_rest_framework_extensions.paginators.DefaultPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'PAGE_SIZE': 10,
    'URL_FORMAT_OVERRIDE': None,
    'DEFAULT_THROTTLE_RATES': {
        'user': '60/minute',
        'service_user': '800/minute',
        'registration_validation': '30/minute',
    },
}


# ------------external plugins configuration backends----------------

EOX_THEMING_CONFIGURATION_HELPER_BACKEND = 'eox_theming.edxapp_wrapper.backends.j_configuration_helpers_tests'
EOX_THEMING_THEMING_HELPER_BACKEND = 'eox_theming.edxapp_wrapper.backends.j_theming_helpers_tests'
EOX_THEMING_EDXMAKO_BACKEND = 'eox_theming.edxapp_wrapper.backends.j_mako_tests'
EOX_THEMING_BASE_LOADER_BACKEND = 'eox_theming.edxapp_wrapper.backends.j_loaders_tests'
EOX_THEMING_CONFIG_SOURCES = [
    'from_django_settings',
]

EOX_CORE_COURSEWARE_BACKEND = "eox_nelp.edxapp_wrapper.test_backends.courseware_m_v1"
EOX_CORE_GRADES_BACKEND = "eox_nelp.edxapp_wrapper.test_backends.grades_m_v1"

# ------------eox-audit external config for tests------------------------------
if find_spec('eox_audit_model') and EOX_AUDIT_MODEL_APP not in INSTALLED_APPS:  # noqa: F405
    INSTALLED_APPS.append(EOX_AUDIT_MODEL_APP)  # noqa: F405
ALLOW_EOX_AUDIT_MODEL = False
CELERY_TASK_ALWAYS_EAGER = True
