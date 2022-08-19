"""
App configuration for eox_nelp.
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class eoxNelpConfig(AppConfig):
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
            'cms.djangoapp': {
                'namespace': 'eox-nelp',
                'regex': r'^eox-nelp/',
                'relative_path': 'urls',
            }
        },
        'settings_config': {
            'lms.djangoapp': {
                'test': {'relative_path': 'settings.test'},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
                'devstack': {'relative_path': 'settings.devstack'},
            },
            'cms.djangoapp': {
                'common': {'relative_path': 'settings.common'},
                'test': {'relative_path': 'settings.test'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }
