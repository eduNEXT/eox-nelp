"""Tasks that represent the logic of some work or undertaken that
signals receivers can use for external_certificates.
"""
import json
import logging

from celery import shared_task
from django.conf import settings
from nelc_api_clients.clients.certificates import ExternalCertificatesApiClient
from sqs_event_publisher.sqs_client import SQSClient

logger = logging.getLogger(__name__)


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
