# Configuration file for the Sphinx documentation builder.

import os
import sys
from pathlib import Path

# Add eox-nelp to Python path
doc_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(doc_path))

# -- Project information -----------------------------------------------------
project = 'eox-nelp'
copyright = '2024, eduNEXT'
author = 'eduNEXT'

# The full version, including alpha/beta/rc tags
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinxcontrib.httpdomain',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
exclude_patterns = []

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# -- Extension configuration -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
    'openedx': ('https://edx.readthedocs.io/projects/edx-platform-api/en/latest/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Enable automatic API documentation generation
autosummary_generate = True
add_module_names = False

# Mock imports for external dependencies
autodoc_mock_imports = [
    'django',
    'rest_framework',
    'edx_rest_framework_extensions',
    'edxmako',
    'openedx',
    'common',
    'completion',
    'courseware',
    'lms',
    'student',
    'xmodule',
]

# Add any Sphinx extension module names here, as strings
todo_include_todos = True

def setup(app):
    """Set up the Sphinx application."""
    # Add custom configuration here if needed
    pass
