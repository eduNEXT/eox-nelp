"""This is a mixin file that allows to reuse test cases.

Classes:
    BaseCourseObjectTestCaseMixin: Test mixin for children classes of BaseCourseObjectTransformerMixin.
    BaseModuleObjectTestCaseMixin: Test mixin for children classes of BaseModuleObjectTransformerMixin.
"""
from mock import Mock, call, patch
from opaque_keys.edx.keys import UsageKey
from tincan import ActivityDefinition, LanguageMap

from eox_nelp.edxapp_wrapper.event_routing_backends import constants
from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.processors.xapi import constants as eox_nelp_constants


class BaseCourseObjectTestCaseMixin:
    """This is a test mixin for classes which implements the BaseCourseObjectTransformerMixin mixin."""

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        self.transformer_class.get_data.reset_mock()
        self.transformer_class.get_data.side_effect = None
        self.transformer_class.get_object_iri.reset_mock()

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
                type=constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap({course["language"]: course["display_name"]}),
                description=LanguageMap({course["language"]: course["short_description"]}),
            ),
            activity.definition,
        )

    @patch("eox_nelp.processors.xapi.mixins.get_course_from_id")
    def test_get_object_method_with_default_language(self, get_course_mock):
        """ Test case that verifies that the object returned uses 'en-US' instead of 'en'

        Expected behavior:
            - Activity definition is the expected value.
        """
        course_id = "course-v1:edx+CS105+2023-T3"
        self.transformer_class.get_data.return_value = course_id
        object_id = f"http://example.com/courses/{course_id}"
        self.transformer_class.get_object_iri.return_value = object_id
        course = {
            "display_name": "great-course",
            "language": "en",
            "short_description": "This is the best course",
        }
        get_course_mock.return_value = course
        transformer = self.transformer_class()

        activity = transformer.get_object()

        self.assertEqual(
            ActivityDefinition(
                type=constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap({eox_nelp_constants.DEFAULT_LANGUAGE: course["display_name"]}),
                description=LanguageMap({eox_nelp_constants.DEFAULT_LANGUAGE: course["short_description"]}),
            ),
            activity.definition,
        )


class BaseModuleObjectTestCaseMixin:
    """This is a test mixin for classes which implements the BaseModuleObjectTransformerMixin class."""

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        self.transformer_class.get_data.reset_mock()
        self.transformer_class.get_data.side_effect = None
        self.transformer_class.get_object_iri.reset_mock()
        modulestore.reset_mock()
        modulestore.return_value.get_item.reset_mock()

    def test_course_id_property(self):
        """Test case that checks that the course_id property has been overridden and returns the expected value.

        Expected behavior:
            - course_id is the expected value.
            - get_data has been called with the right parameters.
        """
        course_id = "course-v1:edx+CS247+2024-T3"
        self.transformer_class.get_data.return_value = course_id
        transformer = self.transformer_class()

        self.assertEqual(course_id, transformer.course_id)
        self.transformer_class.get_data.assert_called_once_with("data.course_id", required=True)

    @patch("eox_nelp.processors.xapi.mixins.get_course_from_id")
    def test_get_object_method(self, get_course_mock):
        """ Test case that verifies that the get_object method returns the expected Activity
        when all the course attributes are found.

        Expected behavior:
            - Activity id is the expected value.
            - get_course_from_id method is called with the right value.
            - get_object_iri method is called with the right value.
            - modulestore get_item methods is called with the right value
            - get_data method is called twice with right values.
            - Activity definition is the expected value.
        """
        # Set get_data returned values
        course_id = "course-v1:edx+CS105+2023-T3"
        item_id = "block-v1:edx+CS104+2023+type@vertical+block@cbf124449a7a46cd82270b6051d6e902"
        self.transformer_class.get_data.side_effect = [item_id, course_id]

        # Set modulestore mock
        item = Mock()
        item.display_name = "Unit"
        modulestore.return_value.get_item.return_value = item

        # Set get_object_iri mock
        object_id = f"http://example.com/xblock/{item_id}"
        self.transformer_class.get_object_iri.return_value = object_id

        # Set get_course_from_id mock
        course = {
            "language": "fr",
        }
        get_course_mock.return_value = course

        # Initialize test class
        transformer = self.transformer_class()

        activity = transformer.get_object()

        self.assertEqual(object_id, activity.id)
        get_course_mock.assert_called_once_with(course_id)
        self.transformer_class.get_object_iri.assert_called_once_with("xblock", item_id)
        modulestore.return_value.get_item.assert_called_once_with(UsageKey.from_string(item_id))
        self.assertEqual(
            [call("data.item_id", required=True), call("data.course_id", required=True)],
            self.transformer_class.get_data.call_args_list,
        )
        self.assertEqual(
            ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                name=LanguageMap({course["language"]: item.display_name}),
            ),
            activity.definition,
        )

    @patch("eox_nelp.processors.xapi.mixins.get_course_from_id")
    def test_get_object_method_with_default_language(self, get_course_mock):
        """ Test case that verifies that the object returned uses 'en-US' instead of 'en'

        Expected behavior:
            - Activity definition is the expected value.
        """
        # Set get_data returned values
        course_id = "course-v1:edx+CS105+2023-T3"
        item_id = "block-v1:edx+CS104+2023+type@vertical+block@cbf124449a7a46cd82270b6051d6e902"
        self.transformer_class.get_data.side_effect = [item_id, course_id]

        # Set modulestore mock
        item = Mock()
        item.display_name = "Unit"
        modulestore.return_value.get_item.return_value = item

        # Set get_object_iri mock
        object_id = f"http://example.com/xblock/{item_id}"
        self.transformer_class.get_object_iri.return_value = object_id

        # Set get_course_from_id mock
        course = {
            "language": "en",
        }
        get_course_mock.return_value = course

        # Initialize test class
        transformer = self.transformer_class()

        activity = transformer.get_object()

        self.assertEqual(
            ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                name=LanguageMap({eox_nelp_constants.DEFAULT_LANGUAGE: item.display_name}),
            ),
            activity.definition,
        )
