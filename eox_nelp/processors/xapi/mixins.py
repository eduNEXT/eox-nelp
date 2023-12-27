"""Mixin file, this is a collection of classes that could be reused in multiple implementations.

Classes:
    - BaseCourseObjectTransformerMixin: Base mixin for transformers that has as object an edx-platform course
"""
from django.utils.functional import cached_property
from opaque_keys.edx.keys import UsageKey
from tincan import Activity, ActivityDefinition, LanguageMap

from eox_nelp.edxapp_wrapper.event_routing_backends import constants
from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.processors.xapi import constants as eox_nelp_constants
from eox_nelp.utils import get_course_from_id


class BaseCourseObjectTransformerMixin:
    """
    Base mixin for transformers that has as object an edx-platform course.
    """
    @cached_property
    def course_id(self):
        """The course id data depends on the kind of event, an event could publish this as course_id or course_key
        so this a wrapper that should be implemented in order to use the get_object method.

        Raises:
            NotImplementedError: when the subclass has not overridden the course_id property.
        """
        raise NotImplementedError("The property course_id has not been implemented, please set this porperty")

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        course = get_course_from_id(self.course_id)
        display_name = course["display_name"]
        description = course["short_description"]
        course_language = course["language"]

        # Set default value if language is not found
        if not course_language or course_language == constants.EN:
            course_language = eox_nelp_constants.DEFAULT_LANGUAGE

        return Activity(
            id=self.get_object_iri("courses", self.course_id),
            definition=ActivityDefinition(
                type=eox_nelp_constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap(**({course_language: display_name} if display_name is not None else {})),
                description=LanguageMap(**({course_language: description} if description is not None else {})),
            ),
        )

    def get_context_activities(self):
        """The XApiTransformer class implements this method and returns in the parent key
        an activity that contains the course metadata however this is not necessary in
        cases where a transformer uses the course metadata as object since the data is
        redundant and a course cannot be its own parent, therefore this must return None.

        Returns:
            None
        """
        return None


class BaseModuleObjectTransformerMixin:
    """
    Base mixin for transformers that has as object an edx-platform module(chapter, sequential, vertical, component).
    """
    @cached_property
    def course_id(self):
        """The course id data depends on the kind of event, an event could publish this as course_id or course_key
        so this a wrapper that should be implemented in order to use the get_object method.

        Raises:
            NotImplementedError: when the subclass has not overridden the course_id property.
        """
        raise NotImplementedError

    @cached_property
    def item_id(self):
        """The item id data depends on the kind of event, an event could publish this as course_id or course_key
        so this a wrapper that should be implemented in order to use the get_object method.

        Raises:
            NotImplementedError: when the subclass has not overridden the course_id property.
        """
        raise NotImplementedError

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        item = modulestore().get_item(UsageKey.from_string(self.item_id))
        display_name = item.display_name

        course = get_course_from_id(self.course_id)
        course_language = course["language"]

        # Set default value if language is not found
        if not course_language or course_language == constants.EN:
            course_language = eox_nelp_constants.DEFAULT_LANGUAGE

        return Activity(
            id=self.get_object_iri("xblock", self.item_id),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                name=LanguageMap(**({course_language: display_name} if display_name is not None else {})),
            ),
        )
