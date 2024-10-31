"""This file contains the test case for nelp courses api view.
AS this is an external plugin using the ancestor class of the CourseApiView,
the fields of that views and serializers are not tested.
This test only test the fields added apart from the other field of the ancestor
class.

TestCases:
- NelpCoursesApiViewsTestCase: test cases for the Nelp views.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from eox_nelp.edxapp_wrapper.course_experience import course_home_url
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.edxapp_wrapper.test_backends.course_api_m_v1 import TEST_RAW_OVERVIEW

User = get_user_model()


class NelpCoursesApiViewsTestCase(APITestCase):
    """ Test Nelp Courses API views. """

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(username="vader", password="vaderpass")
        self.course1 = CourseOverview.objects.create(id=f"{self.BASE_COURSE_ID}1")
        self.course2 = CourseOverview.objects.create(id=f"{self.BASE_COURSE_ID}2")
        self.client.force_authenticate(self.user)

    RESPONSE_CONTENT_TYPES = ["application/json"]
    BASE_COURSE_ID = "course-v1:sky+walker+2023-v"
    reverse_viewname_list = "nelp-course-api:v1:list"
    reverse_viewname_detail = "nelp-course-api:v1:detail"
    expected_overview_object = {
        "about_description": [
            {
                "titles": ["About This Course"],
                "paragraphs": [
                    "The long course description should contain 150-400 words.",
                    "This is paragraph 2 of the long course description. Add more paragraphs as needed.",
                ],
            }
        ],
        "staff": {
            "titles": [[["Course Staff"]]],
            "teachers": [
                {
                    "name": ["Staff Member #1"],
                    "bio": ["Biography of instructor/staff member #1"],
                    "image_url": ["http://testserver/static/images/placeholder-faculty.png"],
                },
                {
                    "name": ["Staff Member #2"],
                    "bio": ["Biography of instructor/staff member #2"],
                    "image_url": ["http://testserver/static/images/placeholder-faculty.png"],
                },
            ],
        },
        "prereqs": [
            {
                "titles": ["Requirements"],
                "paragraphs": ["Add information about the skills and knowledge students need to take this course."],
            }
        ],
        "faq": [
            {
                "h3_questions": ["What web browser should I use?"],
                "p_answers": [
                    "The Open edX platform works best with current versions of: ",
                    "Chrome, Edge, Firefox, Internet Explorer, or Safari.",
                    "See our \nlist of supported browsers for the most up-to-date information.",
                ],
            },
            {"h3_questions": ["Question #2"], "p_answers": ["Your answer would be displayed here."]},
        ],
    }

    def test_get_nelp_courses_list(self):
        """Test a  get for list of nelp courses endpoint.
        Expected behavior:
            - Status code 200.
            - Return expected content types.
            - Return expected content dict, with a pagination and results list of 2 elements.
        """

        url_endpoint = reverse(self.reverse_viewname_list)
        expected_value = {
            "results": [
                {
                    "course_about_url": f"http://testserver/courses/{self.BASE_COURSE_ID}1/about",
                    "course_home_url": course_home_url(f"{self.BASE_COURSE_ID}1"),
                    "overview": TEST_RAW_OVERVIEW,
                    "overview_object": self.expected_overview_object,
                },
                {
                    "course_about_url": f"http://testserver/courses/{self.BASE_COURSE_ID}2/about",
                    "course_home_url": course_home_url(f"{self.BASE_COURSE_ID}2"),
                    "overview": TEST_RAW_OVERVIEW,
                    "overview_object": self.expected_overview_object,
                },
            ],
            "pagination": {"next": None, "previous": None, "count": 2, "num_pages": 1},

        }

        response = self.client.get(url_endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.headers["Content-Type"], self.RESPONSE_CONTENT_TYPES)
        self.assertDictEqual(response.json(), expected_value)

    def test_get_nelp_course_detail(self):
        """Test a  get for a especific course_id of nelp courses endpoint.
        Expected behavior:
            - Status code 200.
            - Return expected content types.
            - Return expected content dict of 1 element.
        """
        course_kwarg = {"course_key_string": f"{self.BASE_COURSE_ID}1"}
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs=course_kwarg)
        expected_value = {
            "course_about_url": f"http://testserver/courses/{self.BASE_COURSE_ID}1/about",
            "course_home_url": course_home_url(f"{self.BASE_COURSE_ID}1"),
            "overview": TEST_RAW_OVERVIEW,
            "overview_object": self.expected_overview_object,
        }

        response = self.client.get(url_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.headers["Content-Type"], self.RESPONSE_CONTENT_TYPES)
        self.assertDictEqual(response.json(), expected_value)
