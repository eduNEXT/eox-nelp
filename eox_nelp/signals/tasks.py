"""Tasks that represent the logic of some work or undertaken that
signals receivers can use.

tasks:
    dispatch_futurex_progress: Logic to post progress data to futurex. It could be sync or async.
    update_mt_training_stage: Updates mt training stage.
    course_completion_mt_updater: Updates mt training stage based on completion logic.
"""
import json
import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from eox_core.edxapp_wrapper.enrollments import get_enrollment
from eventtracking import tracker
from nelc_api_clients.clients.certificates import ExternalCertificatesApiClient
from nelc_api_clients.clients.futurex import FuturexApiClient
from nelc_api_clients.clients.mt import MinisterOfTourismApiClient
from opaque_keys.edx.keys import UsageKey
from sqs_event_publisher.sqs_client import SQSClient

from eox_nelp.edxapp_wrapper.course_blocks import get_student_module_as_dict
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.edxapp_wrapper.grades import SubsectionGradeFactory
from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.signals.utils import _user_has_passing_grade, get_completed_and_graded, get_completion_summary

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def dispatch_futurex_progress(course_id, user_id, is_complete=None):
    """Dispatch the course progress of a user to Futurex platform.

    Args:
        course_id (str): Unique course identifier.
        user_id (str): User identifier.
        is_complete (bool): Determines is that hast complete the course
    """
    if not getattr(settings, "ACTIVATE_DISPATCH_FUTUREX_PROGRESS", False):
        return

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
    api_client = FuturexApiClient(
        client_id=settings.FUTUREX_CLIENT_ID,
        client_secret=settings.FUTUREX_CLIENT_SECRET,
        base_url=settings.FUTUREX_API_URL,
    )
    response = api_client.send_enrollment_progress(data)

    logger.info(
        "send_futurex_progress --- The data %s was sent to the futurex service host %s. The response was: %s",
        data,
        api_client.base_url,
        response,
    )


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
    completion_summary = get_completion_summary(user, course_id)

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


def create_external_certificate(external_certificate_data, user_id=None, course_id=None):
    """This will create an external NELP certificate base on the input data.
    The certificate could be created directly or using SQS.
    To select the way of the creation of the external_certificate you need
    `USE_SQS_FLOW_FOR_EXTERNAL_CERTIFICATES` setting.
    For SQS case you need the user_id.

    Args:
        external_certificate_data (dict): The data to be sent to the external certificate service.
        user_id(str or int): The id of the user to create the external_certificate.
    """
    if getattr(settings, "USE_SQS_FLOW_FOR_EXTERNAL_CERTIFICATES", False) and user_id:
        trigger_external_certificate_sqs.delay(
            external_certificate_data=external_certificate_data,
            user_id=user_id,
            course_id=course_id,
        )
        return
    create_external_certificate_directly.delay(external_certificate_data=external_certificate_data)


@shared_task
def create_external_certificate_directly(external_certificate_data):
    """This will create an external NELP certificate base on the input data

    Args:
        external_certificate_data (dict): The data to be sent to the external certificate service.
    Logs:
        The process and response from external external certifica provider.
    """
    api_client = ExternalCertificatesApiClient(
        user=settings.EXTERNAL_CERTIFICATES_USER,
        password=settings.EXTERNAL_CERTIFICATES_PASSWORD,
        base_url=settings.EXTERNAL_CERTIFICATES_API_URL,
        extra_headers=settings.EXTERNAL_CERTIFICATES_EXTRA_HEADERS,
    )
    response = api_client.create_external_certificate(external_certificate_data)

    logger.info(
        "The data %s was sent to the external certificate service. The response was: %s",
        external_certificate_data,
        response,
    )


@shared_task
def trigger_external_certificate_sqs(external_certificate_data, user_id, course_id):

    """Manages the creation of an external certificate using a SQS flow.
    Args:
        external_certificate_data (dict): The data to be sent to the external certificate service.
        user_id (str or int): The if of the user associated with the certificate.
        course_id (str or courseOpaqueKey): The course_id associated to the certificate.
    Logs:
        Logs the success or failure of the certificate trigger SQS flow
    Returns:
        None
    """
    user_id = str(user_id)
    course_id = str(course_id)
    message_attributes = {
        "UserId": {"StringValue": user_id, "DataType": "String"},
        "CourseId": {"StringValue": course_id, "DataType": "String"},
        "TriggerDomain": {
            "StringValue": getattr(settings, "LMS_BASE", None) or getattr(settings, "SITE_NAME", None),
            "DataType": "String",
        },
    }

    sqs_client = SQSClient(
        queue_url=settings.SQS_CERTIFICATES_URL,
        aws_access_key_id=settings.SQS_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.SQS_AWS_SECRET_ACCESS_KEY,
    )

    sqs_response = sqs_client.send_message(
        message_body=json.dumps(external_certificate_data),
        message_attributes=message_attributes,
    )

    if sqs_response:
        logger.info(
            "External certificate triggered with  MessageId %s created successfully for user_id %s and course_id %s.",
            sqs_response.get("MessageId"),
            user_id,
            course_id,
        )
    else:
        logger.error(
            "Failed to trigger external certificate for user_id %s and course_id %s. Response: %s",
            user_id,
            course_id,
            sqs_response,
        )


@shared_task
def emit_subsection_attempt_event_task(usage_id, user_id):
    """This emits the event nelc.eox_nelp.grades.subsection.submitted when
    any component of a graded subsection has been attempted.

    Args:
        usage_id (str): component usage id.
        user_id (str): User identifier.
    """
    def get_attempts(subsection):
        """Inner method that returns the total of subsection attempts"""
        attempts = 0

        for unit in subsection.get_children():
            for component in unit.get_children():
                student_module = get_student_module_as_dict(
                    user,
                    usage_key.course_key,
                    component.location,
                )
                attempts += student_module.get("attempts", 0)

        return attempts

    store = modulestore()
    user = User.objects.get(id=user_id)
    usage_key = UsageKey.from_string(usage_id)
    vertical = store.get_item(store.get_parent_location(usage_key))
    subsection = vertical.get_parent()
    course = store.get_course(usage_key.course_key)
    subsection_grade_factory = SubsectionGradeFactory(user, course=course)
    subsection_grade = subsection_grade_factory.create(subsection=subsection, read_only=True, force_calculate=True)

    if subsection_grade.graded:
        tracker.emit(
            "nelc.eox_nelp.grades.subsection.submitted",
            {
                "user_id": user_id,
                "course_id": str(usage_key.context_key),
                "block_id": str(subsection_grade.location),
                "submitted_at": timezone.now().strftime("%Y-%m-%d, %H:%M:%S"),
                "earned": subsection_grade.graded_total.earned,
                "possible": subsection_grade.graded_total.possible,
                "percent": subsection_grade.percent_graded,
                "attempts": get_attempts(subsection),
            }
        )


@shared_task
def update_mt_training_stage(course_id, national_id, stage_result):
    """Sets MinisterOfTourismApiClient and updates the training stage base on the
    input arguments.

    Arguments:
        course_id (str): Unique course identifier.
        national_id (str): User identifier.
        stage_result (int): Representation of pass or fail result, 1 for pass  2 for fail.
    """
    api_client = MinisterOfTourismApiClient(
        user=settings.MINISTER_OF_TOURISM_USER,
        password=settings.MINISTER_OF_TOURISM_PASSWORD,
        base_url=settings.MINISTER_OF_TOURISM_API_URL,
    )

    api_client.update_training_stage(
        course_id=course_id,
        national_id=national_id,
        stage_result=stage_result,
    )


@shared_task
def course_completion_mt_updater(user_id, course_id, stage_result, force_graded=None):
    """This executes the update_mt_training_stage task synchronously based on the following conditions:

        1. incomplete_count is 0, that means that the user has completed the whole course.
        2. force_graded is False and the course is not graded or force_graded is True and the course is graded.

    Arguments:
        course_id (str): Unique course identifier.
        national_id (str): User identifier.
    """
    user = User.objects.get(id=user_id)
    extra_info = getattr(user, "extrainfo", None)
    national_id = extra_info.national_id if extra_info and extra_info.national_id else user.username
    is_complete, graded = get_completed_and_graded(user_id, course_id)

    if not is_complete or (force_graded and not graded) or (not force_graded and graded):
        return

    update_mt_training_stage(
        course_id=course_id,
        national_id=national_id,
        stage_result=stage_result,
    )
