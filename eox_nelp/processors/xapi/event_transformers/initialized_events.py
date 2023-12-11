"""
Transformers for initialized events.

Classes:
    InitializedCourseTransformer: Transformer for the event nelc.eox_nelp.initialized.course
"""

from tincan import Activity, ActivityDefinition, LanguageMap, Verb

from eox_nelp.edxapp_wrapper.event_routing_backends import XApiTransformer, XApiTransformersRegistry, constants
from eox_nelp.processors.xapi import constants as eox_nelp_constants
from eox_nelp.utils import get_course_from_id


@XApiTransformersRegistry.register("nelc.eox_nelp.initialized.course")
class InitializedCourseTransformer(XApiTransformer):
    """
    Transformers for event generated when an student start a course.
    """
    _verb = Verb(
        id=constants.XAPI_VERB_INITIALIZED,
        display=LanguageMap({constants.EN: constants.INITIALIZED}),
    )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        course_id = self.get_data('data.course_id', True)
        object_id = self.get_object_iri('course', course_id)
        course = get_course_from_id(course_id)
        display_name = course["display_name"]
        description = course["short_description"]
        # Set default value if language is not found
        course_language = course["language"] or eox_nelp_constants.DEFAULT_LANGUAGE

        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=eox_nelp_constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap(**({course_language: display_name} if display_name is not None else {})),
                description=LanguageMap(**({course_language: description} if description is not None else {}))
            ),
        )
