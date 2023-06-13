"""Frontend Views file.

Contains all the views for render react views using django templates.
These views render frontend react components from npm like frontend essentials.

classes:
    FeedbackCoursesTemplate: View template that render courses carousel.
"""
from django.views import View

from eox_nelp.templates_config import render_to_response


class FeedbackCoursesTemplate(View):
    """Eoxnelp CoursesFeedbackTemplate view class.

    General feedback courses template.
    """

    def get(self, request):  # pylint: disable=unused-argument
        """Render start html"""
        return render_to_response("feedback_courses.html", {})
