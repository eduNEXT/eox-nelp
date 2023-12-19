"""Mixin file, this is a collection of classes that could be reused in multiple implementations.

Classes:
    - BaseCourseObjectTransformerMixin: Base mixin for transformers that has as object an edx-platform course
"""
from django.utils.functional import cached_property
from tincan import Activity, ActivityDefinition, LanguageMap

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
        # Set default value if language is not found
        course_language = course["language"] or eox_nelp_constants.DEFAULT_LANGUAGE

        return Activity(
            id=self.get_object_iri("courses", self.course_id),
            definition=ActivityDefinition(
                type=eox_nelp_constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap(**({course_language: display_name} if display_name is not None else {})),
                description=LanguageMap(**({course_language: description} if description is not None else {})),
            ),
        )
