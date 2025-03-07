"""Frontend Views file.

Contains all the views for render react views using django templates.
These views render frontend react components from npm like frontend essentials.

classes:
    FeedbackCoursesTemplate: View template that render courses carousel.
"""
from django.views import View

from eox_nelp.edxapp_wrapper.edxmako import edxmako


class FeedbackCoursesTemplate(View):
    """Eoxnelp CoursesFeedbackTemplate view class.

    General feedback courses template.
    """

    def get(self, request):
        """Render start html"""
        return edxmako.shortcuts.render_to_response("feedback_carousel/index.html", {}, "main", request)
