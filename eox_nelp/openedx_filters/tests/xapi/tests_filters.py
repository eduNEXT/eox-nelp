"""This file contains all the test for the filters.py file.

Classes:
    XApiActorFilterTestCase: Tests cases for XApiActorFilter filter class.
    XApiBaseEnrollmentFilterTestCase: Test cases for XApiBaseEnrollmentFilter filter class.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from mock import Mock, patch
from tincan import Activity, ActivityDefinition, Agent, LanguageMap

from eox_nelp.openedx_filters.xapi.filters import DEFAULT_LANGUAGE, XApiActorFilter, XApiBaseEnrollmentFilter

User = get_user_model()


class XApiActorFilterTestCase(TestCase):
    """Test class for XApiActorFilter filter class."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.filter = XApiActorFilter(
            filter_type="event_routing_backends.processors.xapi.transformer.xapi_transformer.get_actor",
            running_pipeline=["eox_nelp.openedx_filters.xapi.filters.XApiActorFilter"],
        )
        self.username = "xapi"
        self.email = "xapi@example.com"
        User.objects.update_or_create(username=self.username, email=self.email)

    def test_user_does_not_exist(self):
        """ Test case when the user is not found by the email.

        Expected behavior:
            - Returned value is the same as the given value.
        """
        email = "invalid-email@example.com"
        actor = Agent(
            mbox=email,
        )

        actor = self.filter.run_filter(transformer=Mock(), result=actor)["result"]

        self.assertEqual(f"mailto:{email}", actor.mbox)

    def test_invalid_configuration(self):
        """ Test case when the actor agent doesn't have the attribute mbox,
        this case happens when the XAPI_AGENT_IFI_TYPE setting is different from mbox.

        Expected behavior:
            - Raises TypeError exception.
        """
        actor = Agent(
            account={"homePage": "https://example.com", "name": "harry-potter"}
        )

        self.assertRaises(TypeError, self.filter.run_filter, actor)

    def test_update_given_actor(self):
        """ Test case when the result is updated with the username.

        Expected behavior:
            - Returned value contains right mbox value.
            - Returned value contains right name value.
        """
        actor = Agent(
            mbox=self.email,
        )

        actor = self.filter.run_filter(transformer=Mock(), result=actor)["result"]

        self.assertEqual(f"mailto:{self.email}", actor.mbox)
        self.assertEqual(self.username, actor.name)


class XApiBaseEnrollmentFilterTestCase(TestCase):
    """Test class for XApiBaseEnrollmentFilter filter class."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.filter = XApiBaseEnrollmentFilter(
            filter_type="event_routing_backends.processors.xapi.enrollment_events.base_enrollment.get_object",
            running_pipeline=["eox_nelp.openedx_filters.xapi.filters.XApiBaseEnrollmentFilter"],
        )

    def test_course_id_not_found(self):
        """ Test case when the course_id cannot be extracted from the Activity id.

        Expected behavior:
            - Returned value is the same as the given value.
        """
        activity = Activity(
            id="https://example.com/course/course-v1-invalid-edx+CS105+2023-T3",
        )

        returned_activity = self.filter.run_filter(transformer=Mock(), result=activity)["result"]

        self.assertEqual(activity, returned_activity)

    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_update_result(self, get_course_mock):
        """ Test case when name and description are updated.

        Expected behavior:
            - Definition name has been updated.
            - Definition description has been updated.
            - get_course_from_id was called with the right parameter.
        """
        course = {
            "display_name": "new-course-name",
            "language": "ar",
            "short_description": "This is a short description",
        }

        get_course_mock.return_value = course
        activity = Activity(
            id="https://example.com/course/course-v1:edx+CS105+2023-T3",
            definition=ActivityDefinition(
                type="testing",
                name=LanguageMap(en="old-course-name"),
            ),
        )

        returned_activity = self.filter.run_filter(transformer=Mock(), result=activity)["result"]

        self.assertEqual({course['language']: course["display_name"]}, returned_activity.definition.name)
        self.assertEqual({course['language']: course["short_description"]}, returned_activity.definition.description)
        get_course_mock.assert_called_once_with("course-v1:edx+CS105+2023-T3")

    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_invalid_language(self, get_course_mock):
        """ Test case when language has not been set.

        Expected behavior:
            - Definition name has been updated with default language.
            - Definition description has been updated with default language.
            - get_course_from_id was called with the right parameter.
        """
        course = {
            "display_name": "new-course-name",
            "language": None,
            "short_description": "This is a short description",
        }

        get_course_mock.return_value = course
        activity = Activity(
            id="https://example.com/course/course-v1:edx+CS105+2023-T3",
            definition=ActivityDefinition(
                type="testing",
                name=LanguageMap(en="old-course-name"),
            ),
        )

        returned_activity = self.filter.run_filter(transformer=Mock(), result=activity)["result"]

        self.assertEqual({DEFAULT_LANGUAGE: course["display_name"]}, returned_activity.definition.name)
        self.assertEqual({DEFAULT_LANGUAGE: course["short_description"]}, returned_activity.definition.description)
        get_course_mock.assert_called_once_with("course-v1:edx+CS105+2023-T3")
