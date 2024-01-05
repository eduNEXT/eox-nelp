"""This file contains all the test for receivers.py file.
Classes:
    CourseGradeChangedProgressPublisherTestCase: Test course_grade_changed_progress_publisher receiver.
    BlockcompletionProgressPublisherTestCase: Test block_completion_progress_publisher receiver.
    IncludeTrackerContextTestCase: Test include_tracker_context receiver.
    UpdateAsyncTrackerContextTestCase: Test update_async_tracker_context receiver.
"""
import unittest

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from eventtracking.tracker import get_tracker
from mock import Mock, patch
from opaque_keys.edx.keys import CourseKey
from openedx_events.data import EventsMetadata
from openedx_events.learning.data import CertificateData, CourseData, UserData, UserPersonalData

from eox_nelp.edxapp_wrapper.test_backends import create_test_model
from eox_nelp.signals import receivers
from eox_nelp.signals.receivers import (
    block_completion_progress_publisher,
    certificate_publisher,
    course_grade_changed_progress_publisher,
    emit_initialized_course_event,
    enrollment_publisher,
    include_tracker_context,
    update_async_tracker_context,
)
from eox_nelp.tests.utils import set_key_values

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
            time=self.metadata.time,
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
            time=self.metadata.time,
            certificate_data=certificate_data,
        )
        create_external_certificate_mock.delay.assert_called_with(
            external_certificate_data=generate_data_mock()
        )
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])


class EnrollmentPublisherTestCase(unittest.TestCase):
    """Test class for enrollment_publisher."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.user, _ = User.objects.update_or_create(
            username="Newt",
            email="newt@example.com"
        )
        self.course_key = CourseKey.from_string("course-v1:test+Cx105+2022_T4")
        profile_data = {
            "name": "Newt Scamander"
        }
        setattr(self.user, "profile", set_key_values(profile_data))
        course_enrollment_data = {
            "user": self.user,
            "created": timezone.now(),
            "mode": "no-id-professional",
            "course_id": self.course_key
        }
        self.course_enrollment = set_key_values(course_enrollment_data)

    @override_settings(ENABLE_CERTIFICATE_PUBLISHER=False)
    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_inactive_behavior(self, create_external_certificate_mock):
        """Test that the asynchronous task wont' be called when the setting is not active.

        Expected behavior:
            - create_external_certificate is not called
        """
        enrollment_publisher(self.course_enrollment)

        create_external_certificate_mock.delay.assert_not_called()

    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_invalid_mode(self, create_external_certificate_mock):
        """Test when the course enrollment has an invalid mode.

        Expected behavior:
            - create_external_certificate is not called.
            - Invalid error was logged.
        """
        invalid_mode = "audit"
        log_info = (
            f"The {invalid_mode} enrollment associated with the user <{self.user.username}>"
            f" and course <{self.course_key}> doesn't have a valid mode and therefore its data won't be published."
        )
        invalid_course_enrollment = self.course_enrollment

        setattr(invalid_course_enrollment, "mode", "audit")

        with self.assertLogs(receivers.__name__, level="INFO") as logs:
            enrollment_publisher(invalid_course_enrollment)

        create_external_certificate_mock.delay.assert_not_called()
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])

    @patch("eox_nelp.signals.receivers.CourseGradeFactory")
    @patch("eox_nelp.signals.receivers._generate_external_certificate_data")
    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_create_call(self, create_external_certificate_mock, generate_data_mock, course_grade_factory_mock):
        """Test when the enrollment mode is valid and the asynchronous task is called

        Expected behavior:
            - _generate_external_certificate_data is called with the right parameters.
            - create_external_certificate is called with the _generate_external_certificate_data output.
            - Info was logged.
        """
        generate_data_mock.return_value = {
            "test": True,
        }
        log_info = (
            f"The no-id-professional enrollment associated with the user <{self.user.username}> and "
            f"course <{self.course_key}> has been already generated and its data will be sent "
            "to the NELC certificate service."
        )
        certificate_data = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=self.user.username,
                    email=self.user.email,
                    name=self.user.profile.name,
                ),
                id=self.user.id,
                is_active=self.user.is_active,
            ),
            course=CourseData(
                course_key=self.course_key,
            ),
            mode=self.course_enrollment.mode,
            grade=0,
            current_status='not-passing',
            download_url='',
            name='',
        )
        course_grade_factory = Mock()
        course_grade_factory.read.return_value = set_key_values({"passed": False, "percent": 0})
        course_grade_factory_mock.return_value = course_grade_factory

        with self.assertLogs(receivers.__name__, level="INFO") as logs:
            enrollment_publisher(self.course_enrollment)

        generate_data_mock.assert_called_with(
            time=self.course_enrollment.created,
            certificate_data=certificate_data,
        )
        create_external_certificate_mock.delay.assert_called_with(
            external_certificate_data=generate_data_mock()
        )
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])

    @override_settings(CERTIFICATE_PUBLISHER_VALID_MODES=["another-mode"])
    @patch("eox_nelp.signals.receivers.CourseGradeFactory")
    @patch("eox_nelp.signals.receivers._generate_external_certificate_data")
    @patch("eox_nelp.signals.receivers.create_external_certificate")
    def test_alternative_mode(self, create_external_certificate_mock, generate_data_mock, course_grade_factory_mock):
        """Test when the CERTIFICATE_PUBLISHER_VALID_MODES setting has an alternative mode.

        Expected behavior:
            - _generate_external_certificate_data is called with the right parameters.
            - create_external_certificate is called with the _generate_external_certificate_data output.
            - Info was logged.
        """
        alternative_mode = "another-mode"
        log_info = (
            f"The {alternative_mode} enrollment associated with the user <{self.user.username}> and "
            f"course <{self.course_key}> has been already generated and its data will be sent "
            "to the NELC certificate service."
        )
        certificate_data = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=self.user.username,
                    email=self.user.email,
                    name=self.user.profile.name,
                ),
                id=self.user.id,
                is_active=self.user.is_active,
            ),
            course=CourseData(
                course_key=self.course_key,
            ),
            mode=alternative_mode,
            grade=0,
            current_status='not-passing',
            download_url='',
            name='',
        )
        alternative_course_enrollment = self.course_enrollment
        setattr(alternative_course_enrollment, "mode", alternative_mode)

        course_grade_factory = Mock()
        course_grade_factory.read.return_value = set_key_values({"passed": False, "percent": 0})
        course_grade_factory_mock.return_value = course_grade_factory

        with self.assertLogs(receivers.__name__, level="INFO") as logs:
            enrollment_publisher(alternative_course_enrollment)

        generate_data_mock.assert_called_with(
            time=self.course_enrollment.created,
            certificate_data=certificate_data,
        )
        create_external_certificate_mock.delay.assert_called_with(
            external_certificate_data=generate_data_mock()
        )
        self.assertEqual(logs.output, [
            f"INFO:{receivers.__name__}:{log_info}"
        ])


class EmitInitializedCourseEventTestCase(unittest.TestCase):
    """Test class for emit_initialized_course_event method."""

    @patch("eox_nelp.signals.receivers.tracker")
    def test_event_is_not_emitted(self, tracker_mock):
        """
        This tests when the user has completed more than one component
        therefore the event is not emitted.

        Expected behavior:
            - user_learning_context_completion_queryset is called with the right values.
            - tracking.emit method is not called.
        """
        instance = Mock()
        instance.user_learning_context_completion_queryset.return_value = [
            "fake_record",
            "fake_record",
            "fake_record",
        ]

        emit_initialized_course_event(instance)

        instance.user_learning_context_completion_queryset.assert_called_once_with(
            instance.user,
            instance.context_key,
        )
        tracker_mock.emit.assert_not_called()

    @patch("eox_nelp.signals.receivers.tracker")
    def test_event_is_emitted(self, tracker_mock):
        """
        This tests when the user has completed more than one component
        therefore the event is not emitted.

        Expected behavior:
            - user_learning_context_completion_queryset is called with the right values.
            - tracking.emit method is called with the right values.
        """
        block = Mock()
        block.user_learning_context_completion_queryset.return_value = [
            "fake_record",
        ]

        emit_initialized_course_event(block)

        block.user_learning_context_completion_queryset.assert_called_once_with(
            block.user,
            block.context_key,
        )
        tracker_mock.emit.assert_called_once_with(
            "nelc.eox_nelp.initialized.course",
            {
                "user_id": block.user_id,
                "course_id": str(block.context_key),
                "block_id": str(block.block_key),
                "modified": block.modified,
                "created": block.created,
            }
        )


class IncludeTrackerContextTestCase(unittest.TestCase):
    """Test class for include_tracker_context method."""

    def test_context_is_included(self):
        """
        This tests that the body kwargs has been updated after the method execution.

        Expected behavior:
            - body kwargs is equal to the tracker context
        """
        body = {"kwargs": {}}  # This is the default value for kwargs
        context = {"This is a fake context": True}

        # Set tracker context
        tracker = get_tracker()

        with tracker.context("this_does_not_matter", context):
            include_tracker_context(body)

        self.assertEqual(context, body["kwargs"]["tracker_context"])


class UpdateAsyncTrackerContextTestCase(unittest.TestCase):
    """Test class for update_async_tracker_context method."""

    def test_context_is_included(self):
        """
        This tests that the tracker context has been updated after the method execution.

        Expected behavior:
            - sender request doesn't have any tracker_context key.
            - the current tracker returns the expected context.
        """
        sender = Mock()
        expected_context = {
            "session_id": "ashjdgjashgdui15647851561",
            "course_id": "course-v1:test+Cx105+2022_T4"
        }
        sender.request = {
            "kwargs": {
                "tracker_context": expected_context
            }
        }
        tracker = get_tracker()

        update_async_tracker_context(sender)

        self.assertEqual(expected_context, tracker.resolve_context())
        self.assertNotIn("tracker_context", sender.request["kwargs"])

        # Following line doesn't affect the current implementation, this
        # just clean the context affected by this test.
        tracker.exit_context("asynchronous_context")
