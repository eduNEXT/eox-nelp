"""
Eox-nelp djangoapp receivers to manage django signals
"""
from completion.models import BlockCompletion
from django.db import models
from django.dispatch import receiver
from lms.djangoapps.course_home_api.progress.views import ProgressTabView
from rest_framework.request import Request
from django.conf import settings
from importlib import import_module
from django.http import HttpRequest
from django.contrib.auth.models import User
from opaque_keys.edx.keys import CourseKey
from crum import get_current_request
from celery import shared_task
from eox_core.edxapp_wrapper.enrollments import  get_enrollment
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
import logging


logger = logging.getLogger(__name__)

@receiver(models.signals.post_save, sender=BlockCompletion)
def send_completion_progress_2_futurex(**kwargs):
    instance = kwargs['instance']
    course_id = str(instance.context_key)
    user_id = instance.user_id
    breakpoint()

    sync_post(course_id, user_id)

    async_post.delay(course_id, user_id)


    breakpoint()

    pass

@shared_task
def async_post(course_id, user_id):
    user = user = User.objects.get(id=user_id)
    request = get_mock_request(user)
    data = get_completion_data_from_progress_tab_view(request, course_id, user_id)
    progress_enrollment_data = generate_progress_enrollment_data(data, user, course_id)




def sync_post(course_id, user_id):
    user = user = User.objects.get(id=user_id)
    request = get_current_request()
    data = get_completion_data_from_progress_tab_view(request, course_id, user_id)
    progress_enrollment_data = generate_progress_enrollment_data(data, user, course_id)


def get_completion_data_from_progress_tab_view(request, course_id, user_id):
    existing_legacy_frontend_setting = getattr(settings, "USE_LEARNING_LEGACY_FRONTEND", None)
    setattr(settings, "USE_LEARNING_LEGACY_FRONTEND", False)
    SpecificProgressTabView = ProgressTabView(request=request, format_kwarg={})
    progress_student_response = SpecificProgressTabView.get(request, course_key_string=course_id, student_id=user_id)
    setattr(settings, "USE_LEARNING_LEGACY_FRONTEND", existing_legacy_frontend_setting) if existing_legacy_frontend_setting else delattr(settings, "USE_LEARNING_LEGACY_FRONTEND")
    data = progress_student_response.data
    logger.info(f"succesfull extraction of completion data for student_id:{user_id} in course_id:{course_id}\n")
    return data


def get_mock_request(user):
    rx = HttpRequest()
    rx.user = user
    rx.META = {'SERVER_NAME': settings.ALLOWED_HOSTS[0], 'HTTP_HOST': settings.ALLOWED_HOSTS[0]}
    session_key = None
    engine = import_module(settings.SESSION_ENGINE)
    rx.session = engine.SessionStore(session_key)
    return rx

def generate_progress_enrollment_data(data, user, course_id):
    completion_summary = data.get('completion_summary', {})
    if completion_summary:
        complete_units = completion_summary["complete_count"]
        incomplete_units = completion_summary["incomplete_count"]
        locked_units = completion_summary["locked_count"]
        total_units = complete_units + incomplete_units + locked_units
        overall_progress = complete_units / total_units
    else:
        overall_progress = None

    user_has_passing_grade = data.get('user_has_passing_grade', False)

    enrollment_query = {
        "username": user.username,
        "course_id": course_id,
    }
    enrollment, errors = get_enrollment(**enrollment_query)
    breakpoint()
    course_overview = CourseOverview.objects.get(id=course_id)

    progress_enrollment_data = {
        "courseId": course_id,
        "userId": getattr(user,'id'),
        "approxTotalCourseHrs": getattr(course_overview, 'effort', None),
        "overallProgress": overall_progress,
        "membershipState": enrollment.get('is_active', None),
        "enrolledAt": enrollment.get('created',None),
        "isCompleted": user_has_passing_grade,
    }

    logger.info(f"Succesfull extraction of progress enrollment_data \n : {progress_enrollment_data}")
    return progress_enrollment_data
