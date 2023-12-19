"""This file contains all the test for the initialized_events.py file.

Classes:
    InitializedCourseTransformerTestCase: Tests cases for InitializedCourseTransformer class.
"""
from django.test import TestCase
from tincan import LanguageMap

from eox_nelp.edxapp_wrapper.event_routing_backends import constants
from eox_nelp.processors.tests.xapi.mixins import BaseCourseObjectTestCaseMixin
from eox_nelp.processors.xapi.event_transformers import InitializedCourseTransformer


class InitializedCourseTransformerTestCase(BaseCourseObjectTestCaseMixin, TestCase):
    """Test class for InitializedCourseTransformer class."""
    transformer_class = InitializedCourseTransformer

    def test_verb_attribute(self):
        """ Test case that checks that the _verb attribute has the right values.

        Expected behavior:
            - Verb id is the expected value.
            - Verb display is the expected value.
        """
        verb = self.transformer_class._verb  # pylint: disable=protected-access

        self.assertEqual(constants.XAPI_VERB_INITIALIZED, verb.id)
        self.assertEqual(LanguageMap({constants.EN: constants.INITIALIZED}), verb.display)

    def test_course_id_property(self):
        """Test case that checks that the course_id property has been overridden and returns the expected value.

        Expected behavior:
            - course_id is the expected value.
            - get_data has been called with the right parameters.
        """
        course_id = "course-v1:edx+CS105+2023-T3"
        self.transformer_class.get_data.return_value = course_id
        transformer = self.transformer_class()

        self.assertEqual(course_id, transformer.course_id)
        self.transformer_class.get_data.assert_called_once_with("data.course_id", required=True)
