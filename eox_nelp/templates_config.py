""" Module to configure the rendering for custom templates to eox-nelp."""
import os

import eox_nelp.course_experience.frontend.templates as course_experience_templates
from eox_nelp.edxapp_wrapper.edxmako import edxmako
from eox_nelp.stats import templates as stats_templates

module_templates_to_include = [
    stats_templates,
    course_experience_templates,
]


def render_to_response(template_name, dictionary=None, namespace='main', request=None, **kwargs):
    """ Custom render_to_response implementation using configurable backend and adding template dir """

    for module in module_templates_to_include:
        path_to_templates = os.path.dirname(module.__file__)
        if path_to_templates not in edxmako.LOOKUP['main'].directories:
            edxmako.paths.add_lookup('main', path_to_templates)
    return edxmako.shortcuts.render_to_response(template_name, dictionary, namespace, request, **kwargs)
