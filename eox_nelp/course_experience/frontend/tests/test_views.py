"""This file contains all the test for the course_experience views.py file.
Classes:
    CourseExperienceFrontendTestCase: Test CourseExperienceFrontendView template.
"""
from django.apps import apps
from django.http import HttpResponse
from django.shortcuts import render
from django.test import TestCase
from django.urls import reverse
from mock import patch
from rest_framework.test import APIClient


class FrontendFeedbackCourseTestCase(TestCase):
    """ Test FeedbackCoursesTemplate view """

    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.url_endpoint = reverse("course-experience-frontend:feedback-courses")

    @patch("eox_nelp.templates_config.edxmako")
    def test_edxmako_render_correct_call(self, edxmako_mock):
        """ Test edxmako functions from edxapp_wrapper are called with the right values.
        Expected behavior:
            - `edxmako_mock.paths.add_lookup` is called with course_experience_template_path.
            (The path of course xp templates is used)
            - The get request to the url_endpoint is using the template `feedback_courses.html`.
        """
        course_experience_template_path = apps.get_app_config('eox_nelp').path + "/course_experience/frontend/templates"
        edxmako_mock.shortcuts.render_to_response.return_value = HttpResponse(content='Template mock')

        self.client.get(self.url_endpoint)

        edxmako_mock.paths.add_lookup.assert_called_with('main', course_experience_template_path)
        edxmako_mock.shortcuts.render_to_response.assert_called_with("feedback_courses.html", {}, 'main', None)

    @patch("eox_nelp.course_experience.frontend.views.render_to_response")
    def test_feedback_course_template_behaviour(self, render_to_response_mock):
        """ The correct rendering of the feedback courses template using the url_endpoint
        for frontend feedback courses.
        Expected behavior:
            - Status code 200.
            - Response has the correct title page.
            - Response has the main div for feedback courses carousel.
            - Response has the correct path to load styles with feedback carrousel css.
            - Response has the correct path to load script with feedback carrousel js.
        """
        render_to_response_mock.return_value = render(None, "feedback_courses.html")

        response = self.client.get(self.url_endpoint)

        self.assertContains(response, '<title>Feedback courses general</title>', status_code=200)
        self.assertContains(response, '<div id="feedback-courses-carousel"></div')
        self.assertContains(response, 'feedback_carousel/css/feedback_carousel.css')
        self.assertContains(response, 'feedback_carousel/js/feedback_carousel.js')
