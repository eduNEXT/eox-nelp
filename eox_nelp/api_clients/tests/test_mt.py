"""This file contains all the test for mt api client file.

Classes:
    TestMinisterOfTourismApiClient: Test for eox-nelp/api_clients/mt.py.
"""
import unittest

from django.conf import settings
from mock import Mock, patch

from eox_nelp.api_clients.mt import MinisterOfTourismApiClient
from eox_nelp.api_clients.tests import TestBasicAuthApiClientMixin


class TestMinisterOfTourismApiClient(TestBasicAuthApiClientMixin, unittest.TestCase):
    """Tests MinisterOfTourismApiClient"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.api_class = MinisterOfTourismApiClient
        self.user = settings.MINISTER_OF_TOURISM_USER
        self.password = settings.MINISTER_OF_TOURISM_PASSWORD

    @patch.object(MinisterOfTourismApiClient, "make_post")
    @patch.object(MinisterOfTourismApiClient, "_authenticate", Mock)
    def test_create_certificate(self, post_mock):
        """Test successful post request.

        Expected behavior:
            - Response is the expected value
        """
        expected_value = {
            "correlationID": "f3e013f8-a9e4-4714-8162-4e3384f81578",
            "responseCode": 100,
            "responseMessage": "The update has been successfully",
            "data": {
                "result": True
            },
            "elapsedTime": 0.2972466
        }
        post_mock.return_value = expected_value
        course_id = "course-v1:FutureX+guide+2023"
        national_id = "1222555888"
        stage_result = 1
        api_client = self.api_class()

        response = api_client.update_training_stage(
            course_id=course_id,
            national_id=national_id,
            stage_result=stage_result,
        )

        self.assertDictEqual(response, expected_value)

        self.assertDictEqual(response, expected_value)
