"""Functions that extend the edx-platform behavior based on Django
signals, to check which method is used, go to the apps.py file and
verify the connections.

Functions:
    block_completion_progress_publisher: it will publish the user progress based on post_save signal.
    course_grade_changed_progress_publisher: it will publish the user progress based on COURSE_GRADE_CHANGED signal.
"""
from eox_nelp.signals.tasks import dispatch_futurex_progress


def block_completion_progress_publisher(instance, **kwargs):  # pylint: disable=unused-argument
    """This receiver is connected to the post_save BlockCompletion signal
    and this will publish the user progress to Futurex platform.

    Args:
        instance<Blockcompletion>: Instance of BlockCompletion model.
    """
    dispatch_futurex_progress.delay(
        course_id=str(instance.context_key),
        user_id=instance.user_id,
    )


def course_grade_changed_progress_publisher(
    user,
    course_key,
    course_grade,
    **kwargs
):  # pylint: disable=unused-argument
    """This receiver is connected to the COURSE_GRADE_CHANGED signal
    and will publish user course progress based on the given data.

    Args:
        user<User>: Instance of Django User model.
        course_key<CourseLocator>: Opaque keys locator used to identify a course.
        course_grade<CourseGrade>: Grading class for a specific course.
    """
    dispatch_futurex_progress(
        course_id=str(course_key),
        user_id=user.id,
        is_complete=course_grade.passed,
    )
