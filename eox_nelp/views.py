# -*- coding: utf-8 -*-
"""The generic views for the exc-core plugin project"""

from __future__ import unicode_literals

import json
from os.path import dirname, realpath
from subprocess import CalledProcessError, check_output

import six
from django.http import HttpResponse, JsonResponse
from eox_theming.configuration import ThemingConfiguration as theming
from rest_framework import status

import eox_nelp
from eox_nelp.edxapp_wrapper.mfe_config_view import MFEConfigView


def info_view(request):
    """
    Basic view to show the working version and the exact git commit of the
    installed app
    """
    try:
        working_dir = dirname(realpath(__file__))
        git_data = six.text_type(check_output(
            ["git", "rev-parse", "HEAD"], cwd=working_dir))
    except CalledProcessError:
        git_data = ""

    response_data = {
        "version": eox_nelp.__version__,
        "name": "eox-nelp",
        "git": git_data.rstrip('\r\n'),
    }
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


class NelpMFEConfigView(MFEConfigView):
    """
    Provides an API endpoint to get the MFE_CONFIG from site configuration with
    nelp extra fields.
    """

    def get(self, request):
        """
        Return the MFE configuration by NELP(adding custom nelp fields).
        """
        base_get_response = super().get(request)

        if base_get_response.status_code != 200:
            return base_get_response

        mfe_config_dict = json.loads(base_get_response.content)
        theme_options = theming.options('THEME_OPTIONS')
        interactive_color = theming.options('interactive_color')
        theme_additions = {
            'THEME_OPTIONS': theme_options,
            'CUSTOM_PRIMARY_COLORS': {'pgn-color-primary-base': interactive_color},
        }
        mfe_config_dict.update(theme_additions)

        return JsonResponse(mfe_config_dict, status=status.HTTP_200_OK)
