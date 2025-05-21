Welcome to eox-nelp's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   modules/installation
   modules/configuration
   modules/features
   modules/api
   modules/development
   modules/changelog

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/modules
   api/course_api
   api/cms_api
   api/course_experience

Overview
--------

eox-nelp is an Open edX plugin developed by eduNEXT that extends the edx-platform functionality without modifying the base platform code.
It provides custom development capabilities and enhanced features for the Open edX platform.

Key Features
-----------

* Course Management
    * Modified courses API endpoint
    * Enhanced course creator functionality
    * Image URL functionality

* Frontend Integration
    * React-based components
    * Frontend-essentials library
    * Modern UI/UX implementation

* Signal Handlers
    * Block completion tracking
    * Course grade changes
    * Certificate creation
    * Enrollment processing
    * Payment notifications

Module Documentation
------------------

The complete API documentation is automatically generated from the source code docstrings.
You can find detailed information about each module, class, and function in the API Reference section.

Key Modules:

* :mod:`eox_nelp.apps` - Core application configuration
* :mod:`eox_nelp.admin` - Admin interface customizations
* :mod:`eox_nelp.course_api` - Course API implementation
* :mod:`eox_nelp.course_experience` - Course experience features
* :mod:`eox_nelp.edxapp_wrapper` - Open edX platform integration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
