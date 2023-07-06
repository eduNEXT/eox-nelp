"""This file contains all the test for the stats views.py file.

Classes:
    GetTenantStatsTestCase: Test get_tenant_stats function based view.
"""
from ddt import data, ddt
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from eox_nelp.stats.views import STATS_QUERY_PARAMS


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

        for query_param in STATS_QUERY_PARAMS:
            self.assertEqual("true", response.context[query_param])

    @data(*STATS_QUERY_PARAMS)
    def test_filter_stat_out(self, query_param):
        """
        Since the default behavior shows all the components this tests that specific component
        is filtered out when the query param is false.

        Expected behavior:
            - Status code 200.
            - template name is as expected.
            - tenant-stats div exist
            - the query param is 'false'
            - CSS was included
            - JS was included
        """
        url_endpoint = f"{reverse('stats:tenant')}?{query_param}=false"

        response = self.client.get(url_endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.template_name, response.templates[0].name)
        self.assertContains(response, '<div id="tenant-stats"></div')
        self.assertEqual("false", response.context[query_param])
        self.assertContains(response, "tenant_stats/css/tenant_stats.css")
        self.assertContains(response, "tenant_stats/js/tenant_stats.js")
