"""Views V1 file.

Contains all the views for the first version of the procedures.

classes:
    StartTemplate: start message.
"""
from django.views import View
from common.djangoapps import edxmako
import os
import eox_nelp.course_experience.frontend.templates as xp_fe_template
# pylint: disable=import-error  #create or use backend

def render_to_response(template_name, dictionary=None, namespace='main', request=None, **kwargs):
    """ Custom render_to_response implementation using configurable backend and adding template dir """
    module_templates_to_include = [
        xp_fe_template,
    ]
    for module in module_templates_to_include:
        path_to_templates = os.path.dirname(module.__file__)
        if path_to_templates not in edxmako.LOOKUP['main'].directories:
            edxmako.paths.add_lookup('main', path_to_templates)
    return edxmako.shortcuts.render_to_response(template_name, dictionary, namespace, request, **kwargs)

class StartTemplate(View):
    """Eoxnelp SignUpSourceProcedure view class.

    General bulk update procedure.
    """

    def get(self, request):  # pylint: disable=unused-argument
        """Render start html"""
        return render_to_response('start.html', {})
