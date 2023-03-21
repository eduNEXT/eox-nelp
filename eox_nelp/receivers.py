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


from celery import shared_task

@receiver(models.signals.post_save, sender=BlockCompletion)
def send_completion_progress_2_futurex(**kwargs):
    instance = kwargs['instance']
    course_key = instance.context_key #  course_id not need to be in string way, course locator
    block_id = str(instance.block_key)
    user_id = instance.user_id
    student = instance.user
    rx = HttpRequest()
    rx.user=student
    meta = {'HTTP_SERVER_NAME': 'nazo.com', 'SERVER_NAME': 'google.com', 'HTTP_HOST': 'ownlms'}
    rx.META=meta
    session_key = None
    engine = import_module(settings.SESSION_ENGINE)
    rx.session = engine.SessionStore(session_key)
    SpecificProgressTabView = ProgressTabView(request=rx, format_kwarg={})

    breakpoint()

    progress_student_response = SpecificProgressTabView.get(rx, course_key_string=str(course_key), student_id=student.id)
    data = progress_student_response.data
    completion_summary = data.get('completion_summary', {})
    user_has_passing_grade = data.get('user_has_passing_grade', {})
    breakpoint()

    # completion_summary = get_course_blocks_completion_summary.__wrapped__(course_key, student)
    # course = get_course_with_access(student, 'load', course_key, check_if_enrolled=False)
    # #course_grade#
    # # The block structure is used for both the course_grade and has_scheduled content fields
    # # So it is called upfront and reused for optimization purposes
    # collected_block_structure = get_block_structure_manager(course_key).get_collected()
    # course_grade = CourseGradeFactory().read(student, collected_block_structure=collected_block_structure)

    # # recalculate course grade from visible grades (stored grade was calculated over all grades, visible or not)
    # course_grade.update(visible_grades_only=True, has_staff_access=is_staff)

    # Get has_scheduled_content data



    # Get user_has_passing_grade data
    # user_has_passing_grade = False
    # if not student.is_anonymous:
    #     user_grade = course_grade.percent
    #     user_has_passing_grade = user_grade >= course.lowest_passing_grade

    pass
