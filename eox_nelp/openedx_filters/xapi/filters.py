"""This file contains all the NELP filters that can be implemented by the event-routing-backends library

Filters:
    XApiActorFilter: Modifies the standard ACtor in order to include the name attribute.
"""
from django.contrib.auth import get_user_model
from openedx_filters import PipelineStep
from tincan import Agent

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

    def run_filter(self, result):  # pylint: disable=arguments-differ
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
