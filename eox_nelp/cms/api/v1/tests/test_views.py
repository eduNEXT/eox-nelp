"""
Test views file.
"""

from django.test import TestCase, override_settings
from rest_framework import status

from eox_nelp.edxapp_wrapper.test_backends.cms_api_m_v1 import COURSE_RUN_TEST_RESPONSE


@override_settings(ROOT_URLCONF="eox_nelp.cms_urls")
class CMSApiRouterView(TestCase):
    """
    Test for cms api Router view.
    """

    def test_view_api_router(self):
        """
        For the studio urls.
        Check the `/api/v1/` endpoint works for cms.
        Expected behavior:
            - Status code 200.
            - Return expected data.
        """
        api_url = "/api/v1/"
        expected_data = {"course_runs": "http://testserver/api/v1/course_runs/"}

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json(), expected_data)


@override_settings(ROOT_URLCONF="eox_nelp.cms_urls")
class CMSCourseRunView(TestCase):
    """
    Test for cms Course Run  view.
    """

    def test_course_run_view(self):
        """
        Check the `/api/v1/course_runs` endpoint works for cms.
        Expected behavior:
            - Status code 200.
            - Return expected data.
        """
        api_url = "/api/v1/course_runs/"
        expected_data = COURSE_RUN_TEST_RESPONSE

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json(), expected_data)
