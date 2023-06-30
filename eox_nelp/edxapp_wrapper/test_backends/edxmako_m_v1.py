from django.shortcuts import render
from mock import MagicMock


def get_edxmako():
    """Test backend for eox_nelp.edxapp_wrapper.backends.edxmako_m_v1.

    Returns:
        Mock class.
    """
    def render_wrapper(template_name, dictionary, namespace, request, **kwargs):
        return render(request, template_name, context=dictionary)

    edxmako = MagicMock()
    edxmako.shortcuts.render_to_response = render_wrapper

    return edxmako
