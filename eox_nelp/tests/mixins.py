"""This file contains mixins for common test.

Classes:
    POSTAuthenticatedTestMixin: Mixin for POST authenticated views.
"""

from ddt import data, ddt
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

NOT_ALLOWED_HTTP_METHODS = ["get", "delete", "patch", "put", "head"]


@ddt
class POSTAuthenticatedTestMixin:
    """Mixin for POST views that requires an authenticated user."""

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across OTP test cases.
        """
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(username="vader")
        self.client.force_authenticate(self.user)

    @data(*NOT_ALLOWED_HTTP_METHODS)
    def test_method_not_allowed(self, method_name):
        """
        Test that an http verb or Method not configured are not ALLOWED.
        Expected behavior:.
            - Status code 405 METHOD_NOT_ALLOWED.
        """
        url_endpoint = reverse(self.reverse_viewname)
        method_caller = getattr(self.client, method_name)

        response = method_caller(url_endpoint, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_not_authenticated_user(self):
        """
        Test disallow by credentials the request to the list endpoint
        for the desired view.
        Expected behavior:
            - Return credentials of session were not provided.
            - Status code 403.
        """
        self.client.force_authenticate(user=None)
        url_endpoint = reverse(self.reverse_viewname)

        response = self.client.post(url_endpoint)

        self.assertContains(
            response,
            "Authentication credentials were not provided",
            status_code=status.HTTP_403_FORBIDDEN,
        )
