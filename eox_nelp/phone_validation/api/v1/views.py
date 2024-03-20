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
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden

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
    if not request.data:
        return HttpResponseForbidden()

    otp = generate_otp_chars(
        length=getattr(settings, "PHONE_VALIDATION_OTP_LENGTH", 8),
        custom_charset=getattr(settings, "PHONE_VALIDATION_OTP_CHARSET", ""),
    )
    # user_otp_key = request.user.username + request.data.phone_number
    # cache.set(
    #     user_otp_key,
    #     otp,
    #     timeout=getattr(settings, "PHONE_VALIDATION_OTP_TIMEOUT", 600)
    # )
    return Response({"message": "Got some data!", "data": request.data})




@api_view(['POST'])
def validate_otp(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})




import random
import string

def generate_otp_chars(length=8, custom_charset=""):
    """Generates a random 8-digit (or custom length) alphanumeric OTP string.

    Args:
        length (int, optional): The desired length of the OTP. Defaults to 8.
        custom_charset (custom charset provided ): Charset to use to select random code.

    Returns:
        str: The generated OTP string.
    """
    allowed_chars = string.ascii_letters + string.digits
    if custom_charset:
        allowed_chars = custom_charset
    otp = ''.join(random.choice(allowed_chars) for _ in range(length))
    return otp
