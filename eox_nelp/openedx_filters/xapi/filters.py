"""This file contains all the NELP filters that can be implemented by the event-routing-backends library

Filters:
    XApiActorFilter: Modifies the standard ACtor in order to include the name attribute.
    XApiBaseEnrollmentFilter: Updates enrollment object definition.
"""
from django.contrib.auth import get_user_model
from openedx_filters import PipelineStep
from tincan import Agent, LanguageMap

from eox_nelp.utils import extract_course_id_from_string, get_course_from_id

User = get_user_model()
DEFAULT_LANGUAGE = "en"


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


class XApiBaseEnrollmentFilter(PipelineStep):
    """This filter is designed to modify object attributes of an enrollment event, this will add
    the description field and will change the name based on the course language.

    How to set:
        OPEN_EDX_FILTERS_CONFIG = {
            "event_routing_backends.processors.xapi.enrollment_events.base_enrollment.get_object": {
                "pipeline": ["eox_nelp.openedx_filters.xapi.filters.XApiBaseEnrollmentFilter"],
                "fail_silently": False,
            },
        }
    """

    def run_filter(self, transformer, result):  # pylint: disable=arguments-differ, unused-argument
        """Modifies name and description attributes of the activity's definition.

        Arguments:
            result <Activity>: Object activity for events related to enrollments.

        Returns:
            Activity: Modified activity.
        """
        course_id = extract_course_id_from_string(result.id)

        if course_id:
            # Get course course data
            course = get_course_from_id(course_id)
            display_name = course["display_name"]
            description = course["short_description"]
            course_language = course["language"] or DEFAULT_LANGUAGE  # Set default value if language is not found

            # Create new attributes based on the course properties
            definition_name = LanguageMap(**({course_language: display_name} if display_name is not None else {}))
            description = LanguageMap(**({course_language: description} if description is not None else {}))

            # Updates current result
            result.definition.name = definition_name
            result.definition.description = description

        return {
            "result": result
        }
