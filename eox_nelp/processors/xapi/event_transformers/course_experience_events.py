"""
Transformers for course experience events.

Classes:
    FeedBackCourseTransformer: Transformer for the event nelc.eox_nelp.course_experience.feedback_course
    FeedBackUnitTransformer: Transformer for the event nelc.eox_nelp.course_experience.feedback_unit
"""
from django.utils.functional import cached_property
from tincan import LanguageMap, Result, Verb

from eox_nelp.edxapp_wrapper.event_routing_backends import XApiTransformer, XApiTransformersRegistry, constants
from eox_nelp.processors.xapi import constants as eox_nelp_constants
from eox_nelp.processors.xapi.mixins import BaseCourseObjectTransformerMixin, BaseModuleObjectTransformerMixin


class BaseFeedBackTransformer(XApiTransformer):
    """
    Base transformer for feedback events.
    """
    _verb = Verb(
        id=eox_nelp_constants.XAPI_VERB_RATED,
        display=LanguageMap({constants.EN: eox_nelp_constants.RATED}),
    )
    additional_fields = ('result', )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        min_score = eox_nelp_constants.MIN_FEEDBACK_SCORE
        max_score = eox_nelp_constants.MAX_FEEDBACK_SCORE
        raw_score = int(self.get_data("data.rating_content") or min_score)
        scaled = raw_score / max_score

        return Result(
            score={
                "scaled": scaled,
                "raw": raw_score,
                "min": min_score,
                "max": max_score,
            },
            response=self.get_data("data.feedback") or ""
        )


@XApiTransformersRegistry.register("nelc.eox_nelp.course_experience.feedback_course")
class FeedBackCourseTransformer(BaseCourseObjectTransformerMixin, BaseFeedBackTransformer):
    """
    Transformers for generated event when an student rates a course.
    """
    @cached_property
    def course_id(self):
        """
        Transformer's property that returns the associated
        course id for the `nelc.eox_nelp.course_experience.feedback_course` event.
        """
        return self.get_data('data.course_id', required=True)


@XApiTransformersRegistry.register("nelc.eox_nelp.course_experience.feedback_unit")
class FeedBackUnitTransformer(BaseModuleObjectTransformerMixin, BaseFeedBackTransformer):
    """
    Transformers for generated event when an student rates an unit.
    """
    @cached_property
    def course_id(self):
        """
        Transformer's property that returns the associated
        course id for the `nelc.eox_nelp.course_experience.feedback_unit` event.
        """
        return self.get_data('data.course_id', required=True)

    @cached_property
    def item_id(self):
        """
        Transformer's property that returns the associated
        item id for the `nelc.eox_nelp.course_experience.feedback_unit` event.
        """
        return self.get_data('data.item_id', required=True)
