Configuration
=============

Plugin Settings
-------------

The eox-nelp plugin provides various backend configurations that can be customized in your Django settings:

.. code-block:: python

    # Course Creators Backend
    EOX_NELP_COURSE_CREATORS_BACKEND = 'eox_nelp.edxapp_wrapper.backends.course_creators_k_v1'

    # Course Overviews Backend
    EOX_NELP_COURSE_OVERVIEWS_BACKEND = 'eox_nelp.edxapp_wrapper.backends.course_overviews_m_v1'

    # Site Configuration
    EOX_NELP_SITE_CONFIGURATION = 'eox_nelp.edxapp_wrapper.backends.site_configuration_m_v1'

    # User API
    EOX_NELP_USER_API = 'eox_nelp.edxapp_wrapper.backends.user_api_m_v1'

    # Authentication
    EOX_NELP_USER_AUTHN = 'eox_nelp.edxapp_wrapper.backends.user_authn_r_v1'

Django App Configuration
----------------------

The plugin is configured as a Django app through the ``EoxNelpConfig`` class:

.. code-block:: python

    class EoxNelpConfig(AppConfig):
        name = 'eox_nelp'
        verbose_name = 'Nelp plugin for custom development.'

URL Configuration
---------------

The plugin configures URLs for both LMS and Studio:

.. code-block:: python

    'url_config': {
        'lms.djangoapp': {
            'namespace': 'eox-nelp',
            'regex': r'^eox-nelp/',
            'relative_path': 'urls',
        },
    }

Settings Configuration
-------------------

Different settings are available for various environments:

.. code-block:: python

    'settings_config': {
        'lms.djangoapp': {
            'test': {'relative_path': 'settings.test'},
            'common': {'relative_path': 'settings.common'},
            'production': {'relative_path': 'settings.production'},
            'devstack': {'relative_path': 'settings.devstack'},
        },
    }

Signal Configuration
------------------

The plugin implements various signal handlers for different events:

.. code-block:: python

    'signals_config': {
        'lms.djangoapp': {
            'relative_path': 'signals.receivers',
            'receivers': [
                {
                    'receiver_func_name': 'block_completion_progress_publisher',
                    'signal_path': 'django.db.models.signals.post_save',
                    'dispatch_uid': 'block_completion_publisher_receviver',
                    'sender_path': 'completion.models.BlockCompletion',
                },
                # ... other signal handlers
            ],
        },
    }
