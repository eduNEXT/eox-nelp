"""This file contains all the test for the course_experience views.py file.
Classes:
    CourseExperienceFrontendTestCase: Test CourseExperienceFrontendView template.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class FrontendFeedbackCourseTestCase(TestCase):
    """ Test FeedbackCoursesTemplate view """

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.url_endpoint = reverse("course-experience-frontend:feedback-courses")

    def test_feedback_course_template_behaviour(self):
        """ The correct rendering of the feedback courses template using the url_endpoint
        for frontend feedback courses.
        Expected behavior:
            - Status code 200.
            - Response has the correct title page.
            - Response has the main div for feedback courses carousel.
            - Response has the correct path to load styles with feedback carrousel css.
            - Response has the correct path to load script with feedback carrousel js.
        """
        response = self.client.get(self.url_endpoint)

        self.assertContains(response, '<title>Feedback courses general</title>', status_code=200)
        self.assertContains(response, '<div id="feedback-courses-carousel"></div')
        self.assertContains(response, 'feedback_carousel/css/feedback_carousel.css')
        self.assertContains(response, 'feedback_carousel/js/feedback_carousel.js')
