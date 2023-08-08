"""This file contains all the test for receivers.py file.
Classes:
    CourseGradeChangedProgressPublisherTestCase: Test course_grade_changed_progress_publisher receiver.
    BlockcompletionProgressPublisherTestCase: Test block_completion_progress_publisher receiver.
"""
import unittest

from django.contrib.auth import get_user_model
from django.test import override_settings
from mock import patch
from opaque_keys.edx.keys import CourseKey
from openedx_events.data import EventsMetadata
from openedx_events.learning.data import CertificateData, CourseData, UserData, UserPersonalData

from eox_nelp.edxapp_wrapper.test_backends import create_test_model
from eox_nelp.signals import receivers
from eox_nelp.signals.receivers import (
    block_completion_progress_publisher,
    certificate_publisher,
    course_grade_changed_progress_publisher,
)

User = get_user_model()


class CourseGradeChangedProgressPublisherTestCase(unittest.TestCase):
    """Test class for course_grade_changed_progress_publisher"""

    @patch("eox_nelp.signals.receivers.dispatch_futurex_progress")
    def test_call_dispatch(self, dispatch_mock):
        """Test when course_grade_changed_progress_publisher is called
        with the required parameters.

        Expected behavior:
            - dispatch_futurex_progress is called with the right values.
        """
        user, _ = User.objects.get_or_create(username="Salazar")
        course_key = CourseKey.from_string("course-v1:test+Cx105+2022_T4")
        course_grade = create_test_model('CourseGrade', 'eox_nelp', __package__, fields={"passed": True})

        course_grade_changed_progress_publisher(user, course_key, course_grade)

        dispatch_mock.assert_called_with(
            course_id=str(course_key),
            user_id=user.id,
            is_complete=True,
        )


class BlockcompletionProgressPublisherTestCase(unittest.TestCase):
    """Test class for block_completion_progress_publisher"""

    @patch("eox_nelp.signals.receivers.dispatch_futurex_progress")
    def test_call_dispatch(self, dispatch_mock):
        """Test when block_completion_progress_publisher is called
        with the required parameters.

        Expected behavior:
            - dispatch_futurex_progress is called with the right values.
        """
        course_key = CourseKey.from_string("course-v1:test+Cx105+2022_T4")
        block_completion = create_test_model(
            "BlockCompletion",
            "eox_nelp",
            __package__,
            fields={"user_id": 13, "context_key": course_key},
        )

        block_completion_progress_publisher(block_completion)

        dispatch_mock.delay.assert_called_with(
            course_id=str(course_key),
            user_id=13,
        )


class CertificatePublisherTestCase(unittest.TestCase):
    """Test class for certificate_publisher."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.username = "Harry"
        self.course_key = CourseKey.from_string("course-v1:test+Cx105+2022_T4")
        self.certificate_data = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=self.username,
                    email="harry@potter.com",
                    name="Harry Potter",
                ),
                id=10,
                is_active=True,
            ),
            course=CourseData(
                course_key=self.course_key,
            ),
            mode="no-id-professional",
            grade=5,
            current_status="downloadable",
            download_url="",
            name="",
        )
        self.metadata = EventsMetadata(
            event_type="org.openedx.learning.certificate.created.v1",
            minorversion=0,
        )

    @override_settings(ENABLE_CERTIFICATE_PUBLISHER=False)
    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_inactive_behavior(self, create_external_certificate_mock):
        """Test that the asynchronous task wont' be called when the setting is not active.

        Expected behavior:
            - create_external_certificate is not called
        """
        certificate_publisher(self.certificate_data, self.metadata)

        create_external_certificate_mock.delay.assert_not_called()

    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_invalid_mode(self, create_external_certificate_mock):
        """Test when the certificate data has an invalid mode.

        Expected behavior:
            - create_external_certificate is not called.
            - Invalid error was logged.
        """
        invalid_mode = "audit"
        log_info = (
            f"The {invalid_mode} certificate associated with the user <{self.username}> and course <{self.course_key}> "
            "doesn't have a valid mode and therefore its data won't be published."
        )

        certificate_data = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=self.username,
                    email="harry@potter.com",
                    name="Harry Potter",
                ),
                id=10,
                is_active=True,
            ),
            course=CourseData(
                course_key=self.course_key,
            ),
            mode=invalid_mode,
            grade=5,
            current_status="downloadable",
            download_url="",
            name="",
        )

        with self.assertLogs(receivers.__name__, level="INFO") as logs:
            certificate_publisher(certificate_data, self.metadata)

        create_external_certificate_mock.delay.assert_not_called()
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])

    @patch("eox_nelp.signals.receivers._generate_external_certificate_data")
    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_create_call(self, create_external_certificate_mock, generate_data_mock):
        """Test when the certificate mode is valid and the asynchronous task is called

        Expected behavior:
            - _generate_external_certificate_data is called with the right parameters.
            - create_external_certificate is called with the _generate_external_certificate_data output.
            - Info was logged.
        """
        generate_data_mock.return_value = {
            "test": True,
        }
        log_info = (
            f"The no-id-professional certificate associated with the user <{self.username}> and "
            f"course <{self.course_key}> has been already generated and its data will be sent "
            "to the NELC certificate service."
        )

        with self.assertLogs(receivers.__name__, level="INFO") as logs:
            certificate_publisher(self.certificate_data, self.metadata)

        generate_data_mock.assert_called_with(
            timestamp=self.metadata.time,
            certificate_data=self.certificate_data,
        )
        create_external_certificate_mock.delay.assert_called_with(
            external_certificate_data=generate_data_mock()
        )
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])

    @override_settings(CERTIFICATE_PUBLISHER_VALID_MODES=["another-mode"])
    @patch("eox_nelp.signals.receivers._generate_external_certificate_data")
    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_alternative_mode(self, create_external_certificate_mock, generate_data_mock):
        """Test when the certificate data has an alternative mode.

        Expected behavior:
            - _generate_external_certificate_data is called with the right parameters.
            - create_external_certificate is called with the _generate_external_certificate_data output.
            - Info was logged.
        """
        alternative_mode = "another-mode"
        log_info = (
            f"The {alternative_mode} certificate associated with the user <{self.username}> and "
            f"course <{self.course_key}> has been already generated and its data will be sent "
            "to the NELC certificate service."
        )
        certificate_data = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=self.username,
                    email="harry@potter.com",
                    name="Harry Potter",
                ),
                id=10,
                is_active=True,
            ),
            course=CourseData(
                course_key=self.course_key,
            ),
            mode=alternative_mode,
            grade=5,
            current_status="downloadable",
            download_url="",
            name="",
        )

        with self.assertLogs(receivers.__name__, level="INFO") as logs:
            certificate_publisher(certificate_data, self.metadata)

        generate_data_mock.assert_called_with(
            timestamp=self.metadata.time,
            certificate_data=certificate_data,
        )
        create_external_certificate_mock.delay.assert_called_with(
            external_certificate_data=generate_data_mock()
        )
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])
