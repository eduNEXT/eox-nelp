"""
App configuration for eox_nelp.
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class EoxNelpConfig(AppConfig):
    """
    Nelp plugin for custom development. configuration.
    """
    name = 'eox_nelp'
    verbose_name = 'Nelp plugin for custom development.'
    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'eox-nelp',
                'regex': r'^eox-nelp/',
                'relative_path': 'urls',
            },
        },
        'settings_config': {
            'lms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
                'devstack': {'relative_path': 'settings.devstack'},
            },
        }
    }

    def ready(self):
        """
        Method to perform actions after apps registry is ended.
        """
        # This is required in order to register the receiver inside handlers module.
        from cms.djangoapps.contentstore.signals import handlers  # pylint: disable=unused-import


class EoxNelpCMSConfig(AppConfig):
    """App configuration"""
    name = 'eox_nelp'
    verbose_name = "Nelp Openedx Extensions"

    plugin_app = {
        'url_config': {
            'cms.djangoapp': {
                'namespace': 'eox-nelp',
                'regex': r'^eox-nelp/',
                'relative_path': 'urls',
            }
        },
        'settings_config': {
            'cms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
                'devstack': {'relative_path': 'settings.devstack'},
            },
        },
    }
