"""
Test views file.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from mock import patch
from rest_framework import status
from rest_framework.test import APIClient

from eox_nelp.edxapp_wrapper.test_backends.cms_api_m_v1 import COURSE_RUN_TEST_RESPONSE

User = get_user_model()


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
    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="vader", password="vaderpass",
        )
        self.client.force_authenticate(self.user)

    def test_get_course_run_view_authenticated(self):
        """
        Check the `/api/v1/course_runs` endpoint works for cms for authenticated user.
        Expected behavior:
            - Status code 200.
            - Return expected data.
        """
        api_url = "/api/v1/course_runs/"
        expected_data = COURSE_RUN_TEST_RESPONSE

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json(), expected_data)

    def test_get_course_run_view_not_authenticated(self):
        """
        Check the `/api/v1/course_runs` endpoint doesnt work for unauthenticated user.
        Expected behavior:
            - Status code 403.
            - Return expected data.
        """
        self.client.force_authenticate(user=None)

        api_url = "/api/v1/course_runs/"
        expected_data = {'detail': 'Authentication credentials were not provided.'}

        response = self.client.get(api_url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(response.json(), expected_data)

    @patch("eox_nelp.cms.api.v1.permissions.roles")
    def test_post_course_run_view_wrong_permissions(self, roles_mock):
        """
        Check the POST `/api/v1/course_runs` endpoint doesnt work with auth
        but wrong permissions.
        Expected behavior:
            - Status code 403.
            - Return expected data.
        """
        api_url = "/api/v1/course_runs/"
        roles_mock.GlobalStaff.return_value.has_user.return_value = False
        roles_mock.OrgInstructorRole.return_value.has_user.return_value = False
        post_courserun_data = {
            "title": "mycourse-from-api2",
            "number": "EDNXAPI2",
            "run": "2023t12",
        }
        expected_data = {'detail': 'You do not have permission to perform this action.'}

        response = self.client.post(api_url, post_courserun_data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(response.json(), expected_data)

    @patch("eox_nelp.cms.api.v1.permissions.roles")
    def test_post_course_run_view_global_staff_role(self, roles_mock):
        """
        Check the POST `/api/v1/course_runs` endpoint works with global_staff role.
        Expected behavior:
            - Status code 201.
            - Return post_course_run_data.
        """
        api_url = "/api/v1/course_runs/"
        roles_mock.GlobalStaff.return_value.has_user.return_value = True
        roles_mock.OrgInstructorRole.return_value.has_user.return_value = False
        post_courserun_data = {
            "title": "mycourse-from-api2",
            "number": "EDNXAPI2",
            "run": "2023t12",
        }

        response = self.client.post(api_url, post_courserun_data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.json(), post_courserun_data)

    @patch("eox_nelp.cms.api.v1.permissions.roles")
    def test_post_course_run_view_org_access_role(self, roles_mock):
        """
        Check the POST `/api/v1/course_runs` endpoint works with org_access role.
        Expected behavior:
            - Status code 201.
            - Return post_course_run_data.
        """
        api_url = "/api/v1/course_runs/"
        roles_mock.GlobalStaff.return_value.has_user.return_value = False
        roles_mock.OrgInstructorRole.return_value.has_user.return_value = True
        post_courserun_data = {
            "title": "mycourse-from-api2",
            "number": "EDNXAPI2",
            "run": "2023t12",
        }

        response = self.client.post(api_url, post_courserun_data)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.json(), post_courserun_data)
