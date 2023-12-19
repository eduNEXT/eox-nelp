"""This is a mixin file that allows to reuse test cases.

Classes:
    BaseCourseObjectTestCaseMixin: Test mixin for children classes of BaseCourseObjectTransformerMixin.
"""
from mock import patch
from tincan import ActivityDefinition, LanguageMap

from eox_nelp.processors.xapi import constants as eox_nelp_constants


class BaseCourseObjectTestCaseMixin:
    """This is a test mixin for classes which implements the BaseCourseObjectTransformerMixin mixin."""

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        self.transformer_class.get_data.reset_mock()
        self.transformer_class.get_object_iri.reset_mock()

    @patch("eox_nelp.processors.xapi.mixins.get_course_from_id")
    def test_get_object_method(self, get_course_mock):
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
        self.transformer_class.get_data.return_value = course_id
        object_id = f"http://example.com/courses/{course_id}"
        self.transformer_class.get_object_iri.return_value = object_id
        course = {
            "display_name": "great-course",
            "language": "fr",
            "short_description": "This is the best course",
        }
        get_course_mock.return_value = course
        transformer = self.transformer_class()

        activity = transformer.get_object()

        self.transformer_class.get_data.assert_called_once_with("data.course_id", required=True)
        self.transformer_class.get_object_iri.assert_called_once_with("courses", course_id)
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
