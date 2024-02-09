"""
Transformers for grading events.

Classes:
    SubsectionSubmittedTransformer: Transformer for the event nelc.eox_nelp.grades.subsection.submitted.
"""
from tincan import ActivityDefinition, Extensions, LanguageMap, Result, Verb

from eox_nelp.edxapp_wrapper.event_routing_backends import XApiTransformersRegistry, constants, event_transformers
from eox_nelp.processors.xapi import constants as eox_nelp_constants


@XApiTransformersRegistry.register("nelc.eox_nelp.grades.subsection.submitted")
class SubsectionSubmittedTransformer(event_transformers.ProblemSubmittedTransformer):
    """Transformer class for the event nelc.eox_nelp.grades.subsection.submitted."""

    additional_fields = ('result', )

    def get_verb(self):
        """
        Get verb for xAPI transformed event.

        Returns:
            `Verb`
        """
        return Verb(
            id=constants.XAPI_VERB_ATTEMPTED,
            display=LanguageMap({eox_nelp_constants.DEFAULT_LANGUAGE: constants.ATTEMPTED}),
        )

    def get_object_id(self):
        """
        Returns the object id.

        Returns:
            <str>: string representation of the block id.
        """
        return self.get_data("data.block_id")

    def get_object_definition(self):
        """
        Returns the object definition.

        Returns:
            ActivityDefinition
        """
        return ActivityDefinition(
            type=eox_nelp_constants.XAPI_ACTIVITY_UNIT_TEST
        )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        earned = self.get_data("data.earned") or 0
        possible = self.get_data("data.possible") or 0

        return Result(
            success=earned >= possible,
            score={
                "min": 0,
                "max": possible,
                "raw": earned,
                "scaled": self.get_data("data.percent") or 0,
            }
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.
        Returns:
            `Context`
        """
        context = super().get_context()

        attempts_extension = {
            constants.XAPI_ACTIVITY_ATTEMPT: self.get_data("data.attempts")
        }

        if context.extensions:
            context.extensions.update(attempts_extension)
        else:
            context.extensions = Extensions(attempts_extension)

        return context
