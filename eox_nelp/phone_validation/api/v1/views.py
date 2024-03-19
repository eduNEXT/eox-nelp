# pylint: disable=too-many-lines
"""The generic views for course-experience API. Nelp flavour.
Classes:
- BaseJsonAPIView: General config of rest json api
    - ExperienceView: Config of experience views
        - UnitExperienceView: config for unit-exp views
            - LikeDislikeUnitExperienceView: class-view(`/eox-nelp/api/experience/v1/like/units/`)
            - ReportUnitExperienceView: class-view(`/eox-nelp/api/experience/v1/report/units/`)
        - CourseExperienceView: config for course-exp views
            - LikeDislikeCourseExperienceView: class-view(`/eox-nelp/api/experience/v1/like/courses/`)
            - ReportCourseExperienceView: class-view(`/eox-nelp/api/experience/v1/report/courses/`)
            - FeedbackCourseExperienceView: class-view(`/eox-nelp/api/experience/v1/feedback/courses/`)
    - PublicBaseJsonAPIView: General config of rest json api
        - PublicFeedbackCourseExperienceView: class-view(`/eox-nelp/api/experience/v1/feedback/public/courses/`)
"""
from django.conf import settings
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
try:
    from eox_audit_model.decorators import audit_drf_api
except ImportError:
    def audit_drf_api(*args, **kwargs):  # pylint: disable=unused-argument
        """Identity decorator"""
        return lambda x: x


INVALID_KEY_ERROR = {
    "error": "bad opaque key(item_id or course_id) `InvalidKeyError`"
}


@api_view(['POST'])
def generate_otp(request):

    return Response({"message": "Got some data!", "data": request.data})



@api_view(['POST'])
def validate_otp(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})
