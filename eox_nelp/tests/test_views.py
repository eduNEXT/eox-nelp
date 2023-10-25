"""
Test views file.
"""

from os.path import dirname, realpath
from subprocess import CalledProcessError, check_output

from django.test import TestCase, override_settings
from django.urls import reverse
from mock import patch
from rest_framework import status

import eox_nelp
from eox_nelp import views


class EOXInfoTestCase(TestCase):
    """
    Test for eox-info view.
    """
    def setUp(self):
        """Setup common conditions for every test case"""
        self.url = reverse('eox-info')
        self.view_directory = dirname(realpath(views.__file__))

    def test_view_info_accesible(self):
        """
        This method tests the desired behavior of info_view when this
        does not raise any exception.
        Expected behavior:
            - Return expected content.
            - Status code 200.
        """
        git_data = check_output(['git', 'rev-parse', 'HEAD'], cwd=self.view_directory)
        expected_result = {
            'version': eox_nelp.__version__,
            'name': 'eox-nelp',
            'git': git_data.decode().rstrip('\r\n'),
        }

        response = self.client.get(self.url)

        content = response.json()
        self.assertEqual(expected_result, content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @patch('eox_nelp.views.check_output')
    def test_view_info_response_data(self, check_output_mock):
        """
        This method tests the desired behavior of info_view when
        raise a CalledProcessError exception.
        Expected behavior:
            - check_output called once with the right values.
            - Return expected content.
            - Status code 200.
        """
        check_output_mock.side_effect = CalledProcessError(
            cmd='test-error',
            returncode=0,
        )
        expected_result = {
            'version': eox_nelp.__version__,
            'name': 'eox-nelp',
            'git': '',
        }

        response = self.client.get(self.url)

        content = response.json()
        check_output_mock.assert_called_once_with(
            ['git', 'rev-parse', 'HEAD'],
            cwd=self.view_directory,
        )
        self.assertEqual(expected_result, content)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @override_settings(ROOT_URLCONF='eox_nelp.cms_urls')
    def test_cms_view_info_accesible(self):
        """
        For the studio urls.
        This method tests the same behavior of the test function `test_view_info_accesible`
        but using the cms url config. This ensure that the cms urls has the eox-info view accesible.
        Expected behavior:
            - Same expected  behaviour of `test_view_info_accesible`.
        """
        self.test_view_info_accesible()
