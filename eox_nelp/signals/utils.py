"""Common function for the signals module.

Functions:
    _generate_external_certificate_data: Generates dict data from CertificateData.
    _user_has_passing_grade: Determines if the user has a passing grade
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from eox_core.edxapp_wrapper.courseware import get_courseware_courses
from eox_core.edxapp_wrapper.grades import get_course_grade_factory
from opaque_keys.edx.keys import CourseKey

from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.utils import is_valid_national_id

CourseGradeFactory = get_course_grade_factory()
User = get_user_model()
courses = get_courseware_courses()


def _generate_external_certificate_data(time, certificate_data):
    """This generates a dictionary from a CertificateData class

    Args:
        time<Datetime>: Date when the certificate was created.
        certificate<CertificateData>: This an instance of the class defined in this link
            https://github.com/eduNEXT/openedx-events/blob/main/openedx_events/learning/data.py#L100
            and will provide of the user certificate data.

    Raises:
        KeyError: if the current course has not been set with its group code the method will raise
            this exception.

    Returns:
        Dict: certificate data
    """
    user = User.objects.get(id=certificate_data.user.id)
    group_codes = getattr(settings, "EXTERNAL_CERTIFICATES_GROUP_CODES", {})
    course_id = str(certificate_data.course.course_key)
    extra_info = getattr(user, "extrainfo", None)
    national_id = user.username[:10]  # saml association extra filter

    return {
        "reference_id": generate_reference_id(national_id, course_id),
        "created_at": str(time.date()),
        "expiration_date": None,
        "grade": float(certificate_data.grade) * 100,
        "is_passing": _user_has_passing_grade(user, course_id),
        "group_code": group_codes[course_id],
        "user": {
            "national_id": national_id,
            "english_name": certificate_data.user.pii.name,
            "arabic_name": extra_info.arabic_name if extra_info else "",
        }
    }


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


def generate_reference_id(national_id, course_id):
    """Generate string of reference_id shape.
    Args:
        national_id<string>: Username of the user(national_id).
        course_id<str>: Unique course identifier.

    Returns:
        reference_id<str>: The string of reference_id representation.

    Raise:
        ValueError: National Id is not valid.
    """
    is_valid_national_id(national_id, raise_exception=True)

    return f"{national_id}~{course_id}"


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


def get_completed_and_graded(user_id, course_id):
    """Get the is_complete or is graded info related user and course.
    Returns a tuple with that info.

    Args:
        user_id (str): User id to analize completion and grading.
        course_id (str): CourseId to analize completion and grading.

    Returns:
        is_complete(bool), is_graded(bool): bool flags telling that the course is complete or graded.
    """
    user = User.objects.get(id=user_id)
    course_key = CourseKey.from_string(course_id)
    descriptor = modulestore().get_course(course_key)
    grading_policy = descriptor.grading_policy
    completion_summary = _get_completion_summary(user, course_id)
    is_complete = completion_summary["incomplete_count"] == 0
    is_graded = bool(grading_policy["GRADER"])

    return is_complete, is_graded
