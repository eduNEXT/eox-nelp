"""This file contains all the NELP filters that can be implemented by the event-routing-backends library

Filters:
    XApiActorFilter: Modifies the standard ACtor in order to include the name attribute.
    XApiCourseObjectFilter: Updates course object definition.
    XApiVerbFilter: Updates verba display language key.
"""
from django.contrib.auth import get_user_model
from opaque_keys.edx.keys import UsageKey
from openedx_filters import PipelineStep
from tincan import Agent, LanguageMap

from eox_nelp.edxapp_wrapper.event_routing_backends import constants
from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.processors.xapi.constants import DEFAULT_LANGUAGE
from eox_nelp.utils import extract_course_id_from_string, get_course_from_id, get_item_label

User = get_user_model()


class XApiActorFilter(PipelineStep):
    """This filter modifies the given actor by adding the username.

    Setting XAPI_AGENT_IFI_TYPE = "mbox" is required in order to get the compatible actor, for
    details please check the event-routing-backends library.
    https://github.com/openedx/event-routing-backends/blob/master/event_routing_backends/processors/xapi/transformer.py#L89

    How to set:
        OPEN_EDX_FILTERS_CONFIG = {
            "event_routing_backends.processors.xapi.transformer.xapi_transformer.get_actor": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiActorFilter"],
                "fail_silently": False,
            }
        }
    """

    def run_filter(self, transformer, result):  # pylint: disable=arguments-differ, unused-argument
        """Extracts the email for the given result in order to get the user and returns
        new Agent with email a name.

        Arguments:
            transformer <XApiTransformer>: Transformer instance.
            result <Agent>: default Actor agent of event-routing-backends

        Returns:
            Agent: New agent with name and email if user exist otherwise given agent.
        """
        mbox = result.mbox
        email = mbox.replace("mailto:", "") if "mailto:" in mbox else mbox

        try:
            user = User.objects.get(email=email)
            result = Agent(
                mbox=user.email,
                name=user.username,
            )
        except User.DoesNotExist:
            pass

        return {
            "result": result
        }


class XApiCourseObjectFilter(PipelineStep):
    """This filter is designed to modify object attributes of an event which has a course as object, this will add
    the description field and will change the name based on the course language.

    How to set:
        OPEN_EDX_FILTERS_CONFIG = {
            "event_routing_backends.processors.xapi.enrollment_events.base_enrollment.get_object": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiCourseObjectFilter"],
                "fail_silently": False,
            },
            "event_routing_backends.processors.xapi.completion_events.base_completion.get_object": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiCourseObjectFilter"],
                "fail_silently": False,
            },
            ...
        }
    """

    def run_filter(self, transformer, result):  # pylint: disable=arguments-differ, unused-argument
        """Modifies name and description attributes of the activity's definition.

        Arguments:
            transformer <XApiTransformer>: Transformer instance.
            result <Activity>: Course object activity for any kind of event

        Returns:
            Activity: Modified activity.
        """
        course_id = extract_course_id_from_string(result.id)

        if course_id and result.definition.type == constants.XAPI_ACTIVITY_COURSE:
            # Get course course data
            course = get_course_from_id(course_id)
            display_name = course["display_name"]
            description = course["short_description"]
            course_language = course.get("language")

            # Set default value if language is not found
            if not course_language or course_language == constants.EN:
                course_language = DEFAULT_LANGUAGE

            # Create new attributes based on the course properties
            definition_name = LanguageMap(**({course_language: display_name} if display_name is not None else {}))
            description = LanguageMap(**({course_language: description} if description is not None else {}))

            # Updates current result
            result.definition.name = definition_name
            result.definition.description = description

        return {
            "result": result
        }


class XApiModuleQuestionObjectFilter(PipelineStep):
    """This filter is designed to modify object attributes of events whose object type is a module
    or a question, this will add the description field and will change the name based on the course language.

    How to set:
        OPEN_EDX_FILTERS_CONFIG = {
            "event_routing_backends.processors.xapi.problem_interaction_events.base_problems.get_object": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiModuleQuestionObjectFilter"],
                "fail_silently": False,
            },
            "event_routing_backends.processors.xapi.progress_events.base_progress.get_object": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiModuleQuestionObjectFilter"],
                "fail_silently": False,
            },
            ...
        }
    """

    def run_filter(self, transformer, result):  # pylint: disable=arguments-differ
        """Modifies name and description attributes of the activity's definition.

        Arguments:
            transformer <XApiTransformer>: Transformer instance.
            result <Activity>: Module or Problem object activity for any kind of event.

        Returns:
            Activity: Modified activity.
        """
        if result.definition.type in [constants.XAPI_ACTIVITY_QUESTION, constants.XAPI_ACTIVITY_MODULE]:
            # Get component data from module descriptor block.
            usage_id = transformer.get_data("data.problem_id") or transformer.get_data("data.block_id")
            usage_key = UsageKey.from_string(usage_id)
            item = modulestore().get_item(usage_key)
            display_name = item.display_name
            label = get_item_label(item)

            # Get course languge block.
            course = get_course_from_id(transformer.get_data('course_id'))
            course_language = course.get("language")

            # Set default value if language is not found
            if not course_language or course_language == constants.EN:
                course_language = DEFAULT_LANGUAGE

            if display_name:
                result.definition.name = LanguageMap({course_language: display_name})

            result.definition.description = LanguageMap(**({course_language: label} if label else {}))

        return {
            "result": result
        }


class XApiVerbFilter(PipelineStep):
    """This filter is designed to update the openedx verb default language from en to en-US.

    How to set:
        OPEN_EDX_FILTERS_CONFIG = {
            "event_routing_backends.processors.xapi.transformer.xapi_transformer.get_verb": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiVerbFilter"],
                "fail_silently": False,
            },
        }
    """

    def run_filter(self, transformer, result):  # pylint: disable=arguments-differ, unused-argument
        """Modifies verb display key to use the eox_nelp default language.

        Arguments:
            transformer <XApiTransformer>: Transformer instance.
            result <Verb>: Verb related to an event.

        Returns:
            Verb: Modified verb.
        """
        if constants.EN in result.display:
            result.display = LanguageMap({DEFAULT_LANGUAGE: result.display[constants.EN]})

        return {
            "result": result
        }
