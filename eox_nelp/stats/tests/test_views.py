"""This file contains all the test for the stats views.py file.

Classes:
    GetTenantStatsTestCase: Test get_tenant_stats function based view.
"""
from ddt import data, ddt
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status


@ddt
class GetTenantStatsTestCase(TestCase):
    """ Test get_tenant_stats function based view."""

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = Client()
        self.template_name = "tenant_stats.html"

    def test_get_default_stats(self):
        """
        Test that the default behavior, that is just render the tenant-stats div

        Expected behavior:
            - Status code 200.
            - template name is as expected.
            - tenant-stats div exist
        """
        url_endpoint = reverse("stats:tenant")

        response = self.client.get(url_endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.template_name, response.templates[0].name)
        self.assertContains(response, '<div id="tenant-stats"></div')

    @data("showVideos", "showCourse", "showProblems", "showInstructors", "showLearners")
    def test_get_specific_stat(self, query_param):
        """
        Test that the view render successfully when a query param is included

        Expected behavior:
            - Status code 200.
            - template name is as expected.
            - tenant-stats div exist
            - the query param is 'true'
            - CSS was included
            - JS was included
        """
        url_endpoint = f"{reverse('stats:tenant')}?{query_param}=true"

        response = self.client.get(url_endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.template_name, response.templates[0].name)
        self.assertContains(response, '<div id="tenant-stats"></div')
        self.assertEqual("true", response.context[query_param])
        self.assertContains(response, "tenant_stats/css/tenant_stats.css")
        self.assertContains(response, "tenant_stats/js/tenant_stats.js")
