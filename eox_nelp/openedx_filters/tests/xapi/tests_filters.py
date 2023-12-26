"""This file contains all the test for the filters.py file.

Classes:
    XApiActorFilterTestCase: Tests cases for XApiActorFilter filter class.
    XApiBaseEnrollmentFilterTestCase: Test cases for XApiBaseEnrollmentFilter filter class.
    XApiBaseProblemsFilterTestCase: Test cases for XApiBaseProblemsFilter filter class.
    XApiVerbFilterTestCase: Test cases for XApiVerbFilter filter class.
"""
from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.test import TestCase
from mock import Mock, patch
from tincan import Activity, ActivityDefinition, Agent, LanguageMap, Verb

from eox_nelp.edxapp_wrapper.event_routing_backends import constants
from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.openedx_filters.xapi.filters import (
    XApiActorFilter,
    XApiBaseEnrollmentFilter,
    XApiBaseProblemsFilter,
    XApiVerbFilter,
)
from eox_nelp.processors.xapi.constants import DEFAULT_LANGUAGE

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


@ddt
class XApiBaseProblemsFilterTestCase(TestCase):
    """Test class for XApiBaseProblemsFilterr filter class."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.default_values = {
            "display_name": "testing-course",
            "data.problem_id": "block-v1:edx+CS105+2023-T3+type@problem+block@0221040b086c4618b6b2b2a554558",
            "course_id": "course-v1:edx+CS105+2023-T3",
        }
        self.filter = XApiBaseProblemsFilter(
            filter_type="event_routing_backends.processors.xapi.problem_interaction_events.base_problems.get_object",
            running_pipeline=["eox_nelp.openedx_filters.xapi.filters.XApiBaseProblemsFilter"],
        )
        self.transformer = Mock()
        self.transformer.event = {"name": "edx.grades.problem.submitted"}
        self.transformer.get_data.side_effect = lambda x: self.default_values[x]
        self.transformer._get_submission.return_value = {}  # pylint: disable=protected-access
        self.course = {"language": "ar"}
        self.activity = Activity(
            id="https://example.com/xblock/block-v1:edx+CS105+2023-T3+type@problem+block@0221040b086c4618b6b2b2a554558",
            definition=ActivityDefinition(
                type="http://adlnet.gov/expapi/activities/question",
                name=LanguageMap(en="old-testing-course"),
            ),
        )

        item = Mock()
        item.markdown = ""
        modulestore.return_value.get_item.return_value = item

    def tearDown(self):
        """Restore mocks' state"""
        modulestore.reset_mock()
        self.transformer.reset_mock()

    @data(None, "")
    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_invalid_display_name(self, display_name, get_course_mock):  # pylint: disable=unused-argument
        """ Test case when display_name is None or an empty string.

        Expected behavior:
            - Definition name wasn't updated.
        """
        course_name = "testing-course"
        get_course_mock.return_value = self.course

        # Set results of get_data method.
        self.default_values["display_name"] = display_name
        self.transformer.get_data.side_effect = lambda x: self.default_values[x]

        # Set input arguments.
        self.activity.definition.name = LanguageMap({DEFAULT_LANGUAGE: course_name})

        returned_activity = self.filter.run_filter(transformer=self.transformer, result=self.activity)["result"]

        self.assertEqual({DEFAULT_LANGUAGE: course_name}, returned_activity.definition.name)

    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_valid_display_name(self, get_course_mock):
        """ Test case when display_name is found and valid.

        Expected behavior:
            - Definition name has been updated.
        """
        get_course_mock.return_value = self.course

        returned_activity = self.filter.run_filter(transformer=self.transformer, result=self.activity)["result"]

        self.assertEqual(
            {self.course['language']: self.default_values["display_name"]},
            returned_activity.definition.name,
        )

    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_update_description(self, get_course_mock):
        """ Test case when item label is valid and the description is updated.

        Expected behavior:
            - Definition description has been updated.
        """
        item = Mock()
        label = "This is a great label"
        item.markdown = f">>{label}<<"
        modulestore.return_value.get_item.return_value = item
        get_course_mock.return_value = self.course

        returned_activity = self.filter.run_filter(transformer=self.transformer, result=self.activity)["result"]

        self.assertEqual(
            {self.course['language']: label},
            returned_activity.definition.description,
        )

    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_empty_label(self, get_course_mock):
        """ Test case when the item markdown doesn't contain a label.

        Expected behavior:
            - Definition description is an empty dict.
        """
        get_course_mock.return_value = self.course

        returned_activity = self.filter.run_filter(transformer=self.transformer, result=self.activity)["result"]

        self.assertEqual({}, returned_activity.definition.description)

    @patch("eox_nelp.openedx_filters.xapi.filters.get_course_from_id")
    def test_default_language(self, get_course_mock):
        """ Test case when the course has no language or is not valid.

        Expected behavior:
            - Definition name has the default key language.
        """
        get_course_mock.return_value = {}

        returned_activity = self.filter.run_filter(transformer=self.transformer, result=self.activity)["result"]

        self.assertEqual([DEFAULT_LANGUAGE], list(returned_activity.definition.name.keys()))

    def test_invalid_event(self):
        """ Test case when the event name is different from edx.grades.problem.submitted.

        Expected behavior:
            - Returned activity is the same input activity.
        """
        self.transformer.event = {"name": "other-event"}
        activity = Activity(
            id="empty-activity",
        )

        returned_activity = self.filter.run_filter(transformer=self.transformer, result=activity)["result"]

        self.assertEqual(activity, returned_activity)


@ddt
class XApiVerbFilterTestCaseTestCase(TestCase):
    """Test class for XApiVerbFilterTestCase filter class."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.filter = XApiVerbFilter(
            filter_type="event_routing_backends.processors.xapi.transformer.xapi_transformer.get_verb",
            running_pipeline=["eox_nelp.openedx_filters.xapi.filters.XApiVerbFilter"],
        )

    def test_change_language(self):
        """ Test case when the verb display key is the open edx default value and must be changed

        Expected behavior:
            - Returned verb has the eox-nelp default language.
        """
        display = "any-word"
        verb = Verb(
            id='testing-id',
            display=LanguageMap({constants.EN: display})
        )

        verb = self.filter.run_filter(transformer=Mock(), result=verb)["result"]

        self.assertEqual(display, verb.display[DEFAULT_LANGUAGE])

    @data("fr", "ar", "de", "es")
    def test_keep_language(self, language):
        """ Test case when the verb display key is different from default value.

        Expected behavior:
            - Returned verb has not been modified.
        """
        display = "any-word"
        verb = Verb(
            id='testing-id',
            display=LanguageMap({language: display})
        )

        verb = self.filter.run_filter(transformer=Mock(), result=verb)["result"]

        self.assertEqual(display, verb.display[language])
