"""
Test file for eox_core URLs.
"""
from django.test import TestCase
from django.urls import resolve, reverse

from eox_nelp.eox_core.api.v1.views import NelpEdxappUser

class URLsTestCase(TestCase):
    """Test case for URLs."""

    def test_edxapp_user_url(self):
        """Test that the edxapp-user URL resolves to the correct view.

        Expected behavior:
            - URL name resolves to correct path
            - Path resolves to correct view
        """
        url = reverse('eox-core:v1:edxapp-user')
        self.assertEqual(url, '/eox-core/api/v1/user/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, NelpEdxappUser)
