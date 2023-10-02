"""Functions that extend the edx-platform behavior based on Django
signals, to check which method is used, go to the apps.py file and
verify the connections.

Functions:
    block_completion_progress_publisher: it will publish the user progress based on post_save signal.
    course_grade_changed_progress_publisher: it will publish the user progress based on COURSE_GRADE_CHANGED signal.
    create_course_notifications: this will create upcoming notifications based on the sub-section due dates.
    certificate_publisher: Publish the user certificate data to the NELC certificates service.
"""
import logging

from django.conf import settings
from eox_core.edxapp_wrapper.grades import get_course_grade_factory
from openedx_events.learning.data import CertificateData, CourseData, UserData, UserPersonalData

from eox_nelp.notifications.tasks import create_course_notifications as create_course_notifications_task
from eox_nelp.payment_notifications.models import PaymentNotification
from eox_nelp.signals.tasks import create_external_certificate, dispatch_futurex_progress
from eox_nelp.signals.utils import _generate_external_certificate_data

LOGGER = logging.getLogger(__name__)
CourseGradeFactory = get_course_grade_factory()


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


def create_course_notifications(course_key, **kwargs):  # pylint: disable=unused-argument
    """This receiver is connected to the course_published signal, that belong to
    the class SignalHandler from xmodule, and this will create upcoming notifications
    based on the sub-section due dates.

    Args:
        course_key<CourseLocator>: Opaque keys locator used to identify a course.
    """
    create_course_notifications_task.delay(course_id=str(course_key))


def certificate_publisher(certificate, metadata, **kwargs):  # pylint: disable=unused-argument
    """
    Receiver that is connected to the CERTIFICATE_CREATED signal from 'openedx_events.learning.signals'.

    Basically this verifies that the publish action is active and validates the certificate mode in order
    to publish just certificates with valid modes. That behavior is controlled by the following settings:

    - ENABLE_CERTIFICATE_PUBLISHER<boolean>: If this is true the receiver will publish the certificate data,
    default is False.
    - CERTIFICATE_PUBLISHER_VALID_MODES<list[string]>: List of valid modes, default ['no-id-professional']

    Args:
        certificate<CertificateData>: This an instance of the class defined in this link
            https://github.com/eduNEXT/openedx-events/blob/main/openedx_events/learning/data.py#L100
            and will provide of the user certificate data.
        metadata <EventsMetadata>: Instance of the class defined in this link
            https://github.com/eduNEXT/openedx-events/blob/main/openedx_events/data.py#L29
    """
    if not getattr(settings, "ENABLE_CERTIFICATE_PUBLISHER", False):
        return

    default_modes = [
        "no-id-professional",
    ]
    valid_modes = getattr(settings, "CERTIFICATE_PUBLISHER_VALID_MODES", default_modes)

    if certificate.mode in valid_modes:
        LOGGER.info(
            "The %s certificate associated with the user <%s> and course <%s> has been already generated "
            "and its data will be sent to the NELC certificate service.",
            certificate.mode,
            certificate.user.pii.username,
            certificate.course.course_key,
        )
        create_external_certificate.delay(
            external_certificate_data=_generate_external_certificate_data(
                time=metadata.time,
                certificate_data=certificate,
            )
        )
    else:
        LOGGER.info(
            "The %s certificate associated with the user <%s> and course <%s> "
            "doesn't have a valid mode and therefore its data won't be published.",
            certificate.mode,
            certificate.user.pii.username,
            certificate.course.course_key,
        )


def enrollment_publisher(instance, **kwargs):  # pylint: disable=unused-argument
    """
    Receiver that is connected to the course enrollment post_save signal and this will generate certificate
    data to publish it to the external service. That behavior is controlled by the following settings:

    - ENABLE_CERTIFICATE_PUBLISHER<boolean>: If this is true the receiver will publish the certificate data,
    default is False.
    - CERTIFICATE_PUBLISHER_VALID_MODES<list[string]>: List of valid modes, default ['no-id-professional']

    Note: This keeps the same certificate receiver settings since this will create an external certificate at
    the beginning of the course, then the certificate receiver will update the grade.

    Args:
        instance<CourseEnrollment>: This an instance of the model CourseEnrollment.
    """
    if not getattr(settings, "ENABLE_CERTIFICATE_PUBLISHER", False):
        return

    default_modes = [
        "no-id-professional",
    ]
    valid_modes = getattr(settings, "CERTIFICATE_PUBLISHER_VALID_MODES", default_modes)

    if instance.mode in valid_modes:
        LOGGER.info(
            "The %s enrollment associated with the user <%s> and course <%s> has been already generated "
            "and its data will be sent to the NELC certificate service.",
            instance.mode,
            instance.user.username,
            instance.course_id,
        )
        time = instance.created
        user = instance.user
        course_grade = CourseGradeFactory().read(user, course_key=instance.course_id)
        certificate = CertificateData(
            user=UserData(
                pii=UserPersonalData(
                    username=user.username,
                    email=user.email,
                    name=user.profile.name,
                ),
                id=user.id,
                is_active=user.is_active,
            ),
            course=CourseData(
                course_key=instance.course_id,
            ),
            mode=instance.mode,
            grade=course_grade.percent,
            current_status='downloadable' if course_grade.passed else 'not-passing',
            download_url='',
            name='',
        )

        create_external_certificate.delay(
            external_certificate_data=_generate_external_certificate_data(
                time=time,
                certificate_data=certificate,
            )
        )
    else:
        LOGGER.info(
            "The %s enrollment associated with the user <%s> and course <%s> "
            "doesn't have a valid mode and therefore its data won't be published.",
            instance.mode,
            instance.user.username,
            instance.course_id,
        )


def update_payment_notifications(instance, **kwargs):  # pylint: disable=unused-argument
    """This update the internal status of a payment notification record,
    if the enrollment is active an have the no-id-professional mode this will set
    the internal status as resolution_by_case_1
    """
    if not instance.is_active or instance.mode != "no-id-professional":
        return

    user = instance.user
    course_key = instance.course_id

    payment_notifications = PaymentNotification.objects.filter(  # pylint: disable=no-member
        cdtrans_lms_user_id=user.id,
        cdtrans_course_id=str(course_key),
        internal_status="case_1",
    )

    for payment_notification in payment_notifications:
        payment_notification.internal_status = "resolution_by_case_1"
        payment_notification.save()

        LOGGER.info(
            "The internal status of the payment notification with id %s has been updated to %s",
            payment_notification.id,
            payment_notification.internal_status,
        )
