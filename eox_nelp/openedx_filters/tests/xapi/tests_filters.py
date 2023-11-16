"""This file contains all the test for the filters.py file.

Classes:
    XApiActorFilterTestCase: Tests cases for XApiActorFilter filter class.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from tincan import Agent

from eox_nelp.openedx_filters.xapi.filters import XApiActorFilter

User = get_user_model()


class XApiActorFilterTestCase(TestCase):
    """Test class for XApiActorFilter filter class."""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.filter = XApiActorFilter(
            filter_type="event_routing_backends.processors.xapi.transformer.xapi_transformer.get_actor",
            running_pipeline=["eox_nelp.openedx_filters.xapi.filters.XApiActorFilter"],
        )
        self.username = "xapi"
        self.email = "xapi@example.com"
        User.objects.update_or_create(username=self.username, email=self.email)

    def test_user_does_not_exist(self):
        """ Test case when the user is not found by the email.

        Expected behavior:
            - Returned value is the same as the given value.
        """
        email = "invalid-email@example.com"
        actor = Agent(
            mbox=email,
        )

        actor = self.filter.run_filter(result=actor)["result"]

        self.assertEqual(f"mailto:{email}", actor.mbox)

    def test_invalid_configuration(self):
        """ Test case when the actor agent doesn't have the attribute mbox,
        this case happens when the XAPI_AGENT_IFI_TYPE setting is different from mbox.

        Expected behavior:
            - Raises TypeError exception.
        """
        actor = Agent(
            account={"homePage": "https://example.com", "name": "harry-potter"}
        )

        self.assertRaises(TypeError, self.filter.run_filter, actor)

    def test_update_given_actor(self):
        """ Test case when the result is updated with the username.

        Expected behavior:
            - Returned value contains right mbox value.
            - Returned value contains right name value.
        """
        actor = Agent(
            mbox=self.email,
        )

        actor = self.filter.run_filter(result=actor)["result"]

        self.assertEqual(f"mailto:{self.email}", actor.mbox)
        self.assertEqual(self.username, actor.name)
