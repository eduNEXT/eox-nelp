"""
Transformers for initialized events.

Classes:
    InitializedCourseTransformer: Transformer for the event nelc.eox_nelp.initialized.course
"""

from django.utils.functional import cached_property
from tincan import LanguageMap, Verb

from eox_nelp.edxapp_wrapper.event_routing_backends import XApiTransformer, XApiTransformersRegistry, constants
from eox_nelp.processors.xapi.mixins import BaseCourseObjectTransformerMixin


@XApiTransformersRegistry.register("nelc.eox_nelp.initialized.course")
class InitializedCourseTransformer(BaseCourseObjectTransformerMixin, XApiTransformer):
    """
    Transformers for event generated when an student start a course.
    """
    _verb = Verb(
        id=constants.XAPI_VERB_INITIALIZED,
        display=LanguageMap({constants.EN: constants.INITIALIZED}),
    )

    @cached_property
    def course_id(self):
        """
        Transformer's property that returns the associated
        course id for the `nelc.eox_nelp.initialized.course` event.
        """
        return self.get_data('data.course_id', required=True)
