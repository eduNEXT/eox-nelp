"""Tasks that represent the logic of some work or undertaken that
signals receivers can use.

tasks:
    dispatch_futurex_progress: Logic to post progress data to futurex. It could be sync or async.
"""
import logging

from celery import shared_task
from django.contrib.auth.models import User
from django.db.models import Q
from eox_core.edxapp_wrapper.courseware import get_courseware_courses
from eox_core.edxapp_wrapper.enrollments import get_enrollment
from eox_core.edxapp_wrapper.grades import get_course_grade_factory
from opaque_keys.edx.keys import CourseKey

from eox_nelp.api_clients.futurex import FuturexApiClient
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

courses = get_courseware_courses()
CourseGradeFactory = get_course_grade_factory()
logger = logging.getLogger(__name__)


def _user_has_passing_grade(user, course_id):
    """Determines if a user has passed a course based on the grading policies.

    Args:
        user<User>: Instace of Django User model.
        course_id<str>: Unique course identifier.
    Returns:
        course_grade.passed<bool>: True if the user has passed the course, otherwise False
    """
    course_grade = CourseGradeFactory().read(user, course_key=CourseKey.from_string(course_id))

    return course_grade.passed


@shared_task
def dispatch_futurex_progress(course_id, user_id, is_complete=None):
    """Dispatch the course progress of a user to Futurex platform.

    Args:
        course_id (str): Unique course identifier.
        user_id (str): User identifier.
        is_complete (bool): Determines is that hast complete the course
    """
    user = User.objects.get(id=user_id)
    user_has_passing_grade = is_complete if is_complete is not None else _user_has_passing_grade(user, course_id)

    progress_enrollment_data = _generate_progress_enrollment_data(
        user=user,
        course_id=course_id,
        user_has_passing_grade=user_has_passing_grade,
    )

    _post_futurex_progress(progress_enrollment_data)


def _post_futurex_progress(data):
    """Make post for enrollment http request to FuturexApiClient

    Args:
        data (dict): dict to send to futurex enrollment-progress path.
    """
    api_client = FuturexApiClient()
    response = api_client.enrollment_progress(data)

    logger.info(
        "send_futurex_progress --- The data %s was sent to the futurex service host %s. The response was: %s",
        data,
        api_client.base_url,
        response,
    )


def _get_completion_summary(user, course_id):
    """Get completion summary of a user in a course.

    Args:
        user (User): User object
        course_id (CourseLocator): Unique course identifier.

    Returns:
        completion_summary(dict): Completion summary of the user in the course.
    """
    course_key = CourseKey.from_string(course_id)

    return courses.get_course_blocks_completion_summary(course_key, user)


def _generate_progress_enrollment_data(user, course_id, user_has_passing_grade):
    """Generate the data that with the shape that use progress-enrollment endpoint of futurex.

    Args:
        user (User): User to map the enrollment data.
        course_id (str): Related course to map the enrollment data.
        user_has_passing_grade (bool): bool that check if the user grade pass the course pass grade.
                                                Defaults to False.

    Returns:
        progress_enrollment_data (dict): dict to send to futurex enrollment progress.
    """
    completion_summary = _get_completion_summary(user, course_id)

    if completion_summary:
        complete_units = completion_summary["complete_count"]
        incomplete_units = completion_summary["incomplete_count"]
        locked_units = completion_summary["locked_count"]
        total_units = complete_units + incomplete_units + locked_units
        overall_progress = complete_units / total_units
    else:
        overall_progress = None

    enrollment, _ = get_enrollment(username=user.username, course_id=course_id)
    course_overview = CourseOverview.objects.get(id=course_id)

    social_user = user.social_auth.filter(
        provider="tpa-saml",
    ).exclude(Q(extra_data__isnull=True) | Q(extra_data=None)).first()

    if social_user:
        user_social_id = social_user.extra_data.get("uid")
    else:
        user_social_id = 16734
        logger.error(
            "User:%s doesn't have a social auth record, therefore is not possible to push progress.",
            user,
        )
        # return {}  uncomment after testing

    progress_enrollment_data = {
        "courseId": course_id,
        "userId": user_social_id,
        "approxTotalCourseHrs": getattr(course_overview, "effort", None),
        "overallProgress": overall_progress,
        "membershipState": enrollment.get("is_active", None),
        "enrolledAt": enrollment.get("created", None),
        "isCompleted": user_has_passing_grade,
    }

    logger.info(
        "send_futurex_progress --- Successful extraction of progress_enrollment_data: %s",
        progress_enrollment_data,
    )
    return progress_enrollment_data
