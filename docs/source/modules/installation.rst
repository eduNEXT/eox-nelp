Installation
============

Prerequisites
------------

Before installing eox-nelp, ensure you have the following:

* Open edX instance (Maple release)
* Python environment
* Node.js and npm

Installation Steps
----------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone git@github.com:eduNEXT/eox-nelp.git

2. Install the Plugin
~~~~~~~~~~~~~~~~~~~

Navigate to your Open edX devstack's src folder and install the plugin:

.. code-block:: bash

    cd /path/to/devstack/src
    pip install -e ./eox-nelp

3. Restart Services
~~~~~~~~~~~~~~~~~

Restart the LMS and Studio services to apply the changes.

Frontend Development
------------------

For frontend development, the following commands are available:

Development Mode
~~~~~~~~~~~~~~

.. code-block:: bash

    npm run dev

Production Build
~~~~~~~~~~~~~~

.. code-block:: bash

    npm run build

Dependencies
-----------

Frontend Dependencies
~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

    {
        "@edunext/frontend-essentials": "4.4.0",
        "@edx/brand": "github:nelc/brand-openedx#open-release/redwood.nelp",
        "@edx/frontend-platform": "^7.1.2-alpha-nelc.1",
        "@openedx/paragon": "23.0.0-alpha.1",
        "react": "17.0.2",
        "react-dom": "17.0.2"
    }
