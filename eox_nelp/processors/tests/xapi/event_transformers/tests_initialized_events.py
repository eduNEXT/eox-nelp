"""This file contains all the test for the initialized_events.py file.

Classes:
    InitializedCourseTransformerTestCase: Tests cases for InitializedCourseTransformer class.
"""
from django.test import TestCase
from mock import patch
from tincan import ActivityDefinition, LanguageMap

from eox_nelp.edxapp_wrapper.event_routing_backends import constants
from eox_nelp.processors.xapi import constants as eox_nelp_constants
from eox_nelp.processors.xapi.event_transformers import InitializedCourseTransformer


class InitializedCourseTransformerTestCase(TestCase):
    """Test class for InitializedCourseTransformer class."""

    def test_verb_attribute(self):
        """ Test case that checks that the _verb attribute has the right values.

        Expected behavior:
            - Verb id is the expected value.
            - Verb display is the expected value.
        """
        verb = InitializedCourseTransformer._verb  # pylint: disable=protected-access

        self.assertEqual(constants.XAPI_VERB_INITIALIZED, verb.id)
        self.assertEqual(LanguageMap({constants.EN: constants.INITIALIZED}), verb.display)

    @patch("eox_nelp.processors.xapi.event_transformers.initialized_events.get_course_from_id")
    def test_expected_result(self, get_course_mock):
        """ Test case that verifies that the get_object method returns the expected Activity
        when all the course attributes are found.

        Expected behavior:
            - get_data method is called with the right value.
            - get_object_iri method is called with the right value.
            - get_course_from_id method is called with the right value.
            - Activity id is the expected value.
            - Activity definition is the expected value.

        """
        course_id = "course-v1:edx+CS105+2023-T3"
        InitializedCourseTransformer.get_data.return_value = course_id
        object_id = f"http://example.com/course/{course_id}"
        InitializedCourseTransformer.get_object_iri.return_value = object_id
        course = {
            "display_name": "great-course",
            "language": "fr",
            "short_description": "This is the best course",
        }
        get_course_mock.return_value = course
        transformer = InitializedCourseTransformer()

        activity = transformer.get_object()

        InitializedCourseTransformer.get_data.assert_called_once_with("data.course_id", True)
        InitializedCourseTransformer.get_object_iri.assert_called_once_with("course", course_id)
        get_course_mock.assert_called_once_with(course_id)
        self.assertEqual(object_id, activity.id)
        self.assertEqual(
            ActivityDefinition(
                type=eox_nelp_constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap({course["language"]: course["display_name"]}),
                description=LanguageMap({course["language"]: course["short_description"]}),
            ),
            activity.definition,
        )
