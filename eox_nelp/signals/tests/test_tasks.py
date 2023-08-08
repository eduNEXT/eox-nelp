"""This file contains all the test for tasks.py file.

Classes:
    GetCompletionSummaryTestCase: Test _get_completion_summary method.
    GenerateProgressEnrollmentDataTestCase: Test _generate_progress_enrollment_data method.
"""
import unittest

from ddt import data, ddt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from mock import patch
from opaque_keys.edx.keys import CourseKey
from social_django.models import UserSocialAuth

from eox_nelp.signals import tasks
from eox_nelp.signals.tasks import (
    _generate_progress_enrollment_data,
    _get_completion_summary,
    _post_futurex_progress,
    create_external_certificate,
    dispatch_futurex_progress,
)

User = get_user_model()
FALSY_ACTIVATION_VALUES = [0, "", None, [], False, {}, ()]
TRUTHY_ACTIVATION_VALUES = [1, "true", "activated", ["activated"], True, {"activated": "true"}]


@ddt
class DipatchFuturexProgressTestCase(unittest.TestCase):
    """Test class for function `dispatch_futurex_progress`"""

    @override_settings()
    @patch("eox_nelp.signals.tasks._generate_progress_enrollment_data")
    @patch("eox_nelp.signals.tasks._post_futurex_progress")
    @data(*TRUTHY_ACTIVATION_VALUES)
    def test_call_dispatch_futurex_progress(
        self, truthy_value, post_futurex_progress_mock, generate_progress_enrollment_data_mock,
    ):
        """Test when `dispatch_futurex_progress` is called
        with the required parameters. Check the functions inside are called with
        their desired values. Also with the setting `ACTIVATE_DISPATCH_FUTUREX_PROGRESS` configurated
        with truthy value.

        Expected behavior:
            - `_generate_progress_enrollment_data` is called with the right values.
            - `post_futurex_progress` is called with the right values.
        """
        user, _ = User.objects.get_or_create(username="vader")
        course_id = "course-v1:test+Cx105+2022_T4"
        progress_enrollment_data = {
            "courseId": "course-v1:edX+213+2121",
            "userId": 16734,
            "approxTotalCourseHrs": None,
            "overallProgress": 0.16279069767441862,
            "membershipState": True,
            "enrolledAt": "2023-03-16T20:24:19.494709Z",
            "isCompleted": False,
        }
        generate_progress_enrollment_data_mock.return_value = progress_enrollment_data
        setattr(settings, "ACTIVATE_DISPATCH_FUTUREX_PROGRESS", truthy_value)

        dispatch_futurex_progress(course_id, user.id, is_complete=True)

        generate_progress_enrollment_data_mock.assert_called_with(
            user=user,
            course_id=course_id,
            user_has_passing_grade=True,
        )
        post_futurex_progress_mock.assert_called_with(progress_enrollment_data)

    @override_settings()
    @patch("eox_nelp.signals.tasks._generate_progress_enrollment_data")
    @patch("eox_nelp.signals.tasks._post_futurex_progress")
    def test_not_call_dispatch_logic_setting_not_configured(
        self, post_futurex_progress_mock, generate_progress_enrollment_data_mock
    ):
        """Test `dispatch_futurex_progress` is called but the logic inside not.
        So `generate_progress_enrollment_data` and `post_futurex_progress` are not called
        due no setting configured.

        Expected behavior:
            - generate_progress_enrollment_data is not called due settings.
            - post_futurex_progress_mock is not called due settings.
        """
        user, _ = User.objects.get_or_create(username="vader")
        course_id = "course-v1:test+Cx105+2022_T4"
        if hasattr(settings, "ACTIVATE_DISPATCH_FUTUREX_PROGRESS"):
            delattr(settings, "ACTIVATE_DISPATCH_FUTUREX_PROGRESS")

        dispatch_futurex_progress(course_id, user.id, is_complete=True)

        generate_progress_enrollment_data_mock.assert_not_called()
        post_futurex_progress_mock.assert_not_called()

    @override_settings()
    @patch("eox_nelp.signals.tasks._generate_progress_enrollment_data")
    @patch("eox_nelp.signals.tasks._post_futurex_progress")
    @data(*FALSY_ACTIVATION_VALUES)
    def test_not_call_dispatch_logic_setting_falsy(
        self, falsy_value, post_futurex_progress_mock, generate_progress_enrollment_data_mock,
    ):
        """Test `dispatch_futurex_progress` is called but the logic inside not.
        So `generate_progress_enrollment_data` and `post_futurex_progress` are not called
        due setting configured with falsy value.

        Expected behavior:
            - generate_progress_enrollment_data is not called due settings.
            - post_futurex_progress_mock is not called due settings.
        """
        user, _ = User.objects.get_or_create(username="vader")
        course_id = "course-v1:test+Cx105+2022_T4"
        setattr(settings, "ACTIVATE_DISPATCH_FUTUREX_PROGRESS", falsy_value)

        dispatch_futurex_progress(course_id, user.id, is_complete=True)

        generate_progress_enrollment_data_mock.assert_not_called()
        post_futurex_progress_mock.assert_not_called()


class PostFuturexProgressTestCase(unittest.TestCase):
    """Test class for function `_post_futurex_progress`"""

    @patch("eox_nelp.signals.tasks.FuturexApiClient")
    def test_dispatch_futurex_progress(self, futurex_api_client_mock):
        """Test when `_post_futurex_progress` is called
        with the required parameters. Check the functions inside are called with
        their desired values.

        Expected behavior:
            - FuturexApiClient is used with the right values.
            - Log successful sent to service message.
        """
        progress_enrollment_data = {
            "courseId": "course-v1:edX+213+2121",
            "userId": 16734,
            "approxTotalCourseHrs": None,
            "overallProgress": 0.16279069767441862,
            "membershipState": True,
            "enrolledAt": "2023-03-16T20:24:19.494709Z",
            "isCompleted": False,
        }
        service_base_url = "testingfuturexsink.com"
        service_response = {'status': {'success': True, 'message': 'successful', 'code': 1}}
        log_post = (
            f"send_futurex_progress --- "
            f"The data {progress_enrollment_data} was sent to the futurex service host {service_base_url}. "
            f"The response was: {service_response}"
        )
        futurex_api_client_mock().base_url = service_base_url
        futurex_api_client_mock().enrollment_progress.return_value = service_response

        with self.assertLogs(tasks.__name__, level="INFO") as logs:
            _post_futurex_progress(progress_enrollment_data)

        futurex_api_client_mock().enrollment_progress.assert_called_with(progress_enrollment_data)
        self.assertEqual(logs.output, [f"INFO:{tasks.__name__}:{log_post}"])


class GetCompletionSummaryTestCase(unittest.TestCase):
    """Test class for _get_completion_summary"""

    @patch("eox_nelp.signals.tasks.courses")
    def test_get_course_blocks(self, courses_mock):
        """Test standard call with the required parameters.

        Expected behavior:
            - get_course_blocks_completion_summary is called with the right values.
        """
        user, _ = User.objects.get_or_create(username="Salazar")
        course_id = "course-v1:test+Cx105+2022_T4"
        course_key = CourseKey.from_string(course_id)

        _get_completion_summary(user, course_id)

        courses_mock.get_course_blocks_completion_summary.assert_called_with(course_key, user)


class GenerateProgressEnrollmentDataTestCase(unittest.TestCase):
    """Test class for _generate_progress_enrollment_data."""

    def setUp(self):
        """ Set common conditions for test cases."""
        patcher1 = patch("eox_nelp.signals.tasks._get_completion_summary")
        patcher2 = patch("eox_nelp.signals.tasks.get_enrollment")
        patcher3 = patch("eox_nelp.signals.tasks.CourseOverview")

        self.completion_summary_mock = patcher1.start()
        self.enrollment_mock = patcher2.start()
        self.course_overview_mock = patcher3.start()

        self.lms_user, _ = User.objects.get_or_create(username="Godric")

        self.saml_user, _ = User.objects.get_or_create(username="Salazar")
        self.saml_social_user, _ = UserSocialAuth.objects.get_or_create(
            user=self.saml_user,
            provider="tpa-saml",
            extra_data={"uid": 1313}
        )
        UserSocialAuth.objects.get_or_create(
            user=self.saml_user,
            provider="tpa-saml",
        )
        UserSocialAuth.objects.get_or_create(
            user=self.saml_user,
            provider="okta",
        )

        self.patchers = [patcher1, patcher2, patcher3]

    def tearDown(self):
        """Stop patching."""
        for patcher in self.patchers:
            patcher.stop()

    def test_empty_completion_summary(self):
        """Test when _get_completion_summary returns an empty list.

        Expected behavior:
            - completion_summary is called with the right values.
            - get_enrollment is called with the right values.
            - Log successful message.
            - Returned data is as expected.
        """
        self.completion_summary_mock.return_value = []
        self.enrollment_mock.return_value = (
            {
                "is_active": True,
                "created": "2022-11-01T22:05:47.082806Z"
            },
            None,
        )
        self.course_overview_mock.objects.get.return_value.effort = 10
        course_id = "course-v1:test+Cx105+2022_T4"
        expected_data = {
            "courseId": course_id,
            "userId": self.saml_social_user.extra_data["uid"],
            "approxTotalCourseHrs": 10,
            "overallProgress": None,
            "membershipState": True,
            "enrolledAt": "2022-11-01T22:05:47.082806Z",
            "isCompleted": False,
        }
        log_error = f"send_futurex_progress --- Successful extraction of progress_enrollment_data: {expected_data}"

        with self.assertLogs(tasks.__name__, level="INFO") as logs:
            progress_data = _generate_progress_enrollment_data(self.saml_user, course_id, False)

        self.completion_summary_mock.assert_called_with(self.saml_user, course_id)
        self.enrollment_mock.assert_called_with(username=self.saml_user.username, course_id=course_id)
        self.assertEqual(logs.output, [
            f"INFO:{tasks.__name__}:{log_error}"
        ])
        self.assertDictEqual(expected_data, progress_data)

    def test_populated_completion_summary(self):
        """Test when _get_completion_summary returns a dictionary with the standard data.

        Expected behavior:
            - completion_summary is called with the right values.
            - get_enrollment is called with the right values.
            - Log successful message.
            - Returned data is as expected.
        """
        self.completion_summary_mock.return_value = {
            "complete_count": 15,
            "incomplete_count": 60,
            "locked_count": 5
        }
        self.enrollment_mock.return_value = (
            {
                "is_active": True,
                "created": "2022-11-01T22:05:47.082806Z"
            },
            None,
        )
        self.course_overview_mock.objects.get.return_value.effort = 10
        course_id = "course-v1:test+Cx1985+2022_T4"
        expected_data = {
            "courseId": course_id,
            "userId": self.saml_social_user.extra_data["uid"],
            "approxTotalCourseHrs": 10,
            "overallProgress": 15 / 80,
            "membershipState": True,
            "enrolledAt": "2022-11-01T22:05:47.082806Z",
            "isCompleted": False,
        }
        log_error = f"send_futurex_progress --- Successful extraction of progress_enrollment_data: {expected_data}"

        with self.assertLogs(tasks.__name__, level="INFO") as logs:
            progress_data = _generate_progress_enrollment_data(self.saml_user, course_id, False)

        self.completion_summary_mock.assert_called_with(self.saml_user, course_id)
        self.enrollment_mock.assert_called_with(username=self.saml_user.username, course_id=course_id)
        self.assertEqual(logs.output, [
            f"INFO:{tasks.__name__}:{log_error}"
        ])
        self.assertDictEqual(expected_data, progress_data)

    def test_social_user_not_found(self):
        """Test when the user has no a related social user record.

        Expected behavior:
            - completion_summary is called with the right values.
            - get_enrollment is called with the right values.
            - Log error message.
            - Returned data is as expected.
        """
        self.completion_summary_mock.return_value = []
        self.enrollment_mock.return_value = (
            {
                "is_active": True,
                "created": "2022-11-01T22:05:47.082806Z"
            },
            None,
        )
        self.course_overview_mock.objects.get.return_value.effort = 10
        course_id = "course-v1:test+Cx185+2022_T4"
        expected_data = {
            "courseId": course_id,
            "userId": 16734,
            "approxTotalCourseHrs": 10,
            "overallProgress": None,
            "membershipState": True,
            "enrolledAt": "2022-11-01T22:05:47.082806Z",
            "isCompleted": False,
        }
        log_error = (
            f"User:{self.lms_user} doesn't have a social auth record, therefore is not possible to push progress."
        )

        with self.assertLogs(tasks.__name__, level="ERROR") as logs:
            progress_data = _generate_progress_enrollment_data(self.lms_user, course_id, False)

        self.completion_summary_mock.assert_called_with(self.lms_user, course_id)
        self.enrollment_mock.assert_called_with(username=self.lms_user.username, course_id=course_id)
        self.assertEqual(logs.output, [
            f"ERROR:{tasks.__name__}:{log_error}"
        ])
        self.assertDictEqual(expected_data, progress_data)


class CreateExternalCertificateTestCase(unittest.TestCase):
    """Test class for create_external_certificate function"""

    @patch("eox_nelp.signals.tasks.ExternalCertificatesApiClient")
    def test_certificate_creation(self, api_mock):
        """Test standard call with the required parameters.

        Expected behavior:
            - api_mock was called once.
            - create_external_certificate was called with the rigth parameters.
        """
        certificate_data = {
            "this": "is_a_test",
        }

        create_external_certificate(certificate_data)

        api_mock.assert_called_once()
        api_mock.return_value.create_external_certificate.assert_called_once_with(
            certificate_data
        )
