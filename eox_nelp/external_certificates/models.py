"""
Models file for the external_certificates.
"""
import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

User = get_user_model()
logger = logging.getLogger(__name__)


class ExternalCertificate(models.Model):
    """
    Model to store information about external certificates.

    Attributes:
        user (User): The user associated with the certificate.
        course_overview (str): Course overview associated with the certificate.
        certificate_id (str): Unique identifier of the certificate.
        certificate_url_en (str): URL to access the certificate in English.
        certificate_url_ar (str): URL to access the certificate in Arabic.
        created_at (datetime): Timestamp when the certificate was created.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="external_certificates",
        help_text="The user associated with this certificate.",
    )
    course_overview = models.ForeignKey(
        CourseOverview,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The course overview associated with this certificate.",
    )
    certificate_id = models.CharField(
        max_length=50,
        help_text="Unique identifier for the certificate.",
    )
    certificate_url_en = models.URLField(
        max_length=500,
        help_text="URL for the certificate in English.",
    )
    certificate_url_ar = models.URLField(
        max_length=500,
        help_text="URL for the certificate in Arabic.",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="The date and time when the certificate was created.",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class for ExternalCertificate model.
        """
        verbose_name = "External Certificate"
        verbose_name_plural = "External Certificates"

    def __str__(self):
        return f"Certificate {self.certificate_id} for user {self.user} and course_overview {self.course_overview}"

    @classmethod
    def create_external_certificate_from_certificate_response(cls, certificate_response, user, course_overview):
        """Create an external certificate from the response of the external certificate service.
        Args:
            certificate_response (dict): The response from the external certificate service.
            user (User): The user associated with the certificate.
            course_overview (CourseOverview): Course Overview object associated with the certificate.
        Logs:
            Logs the success or failure of the certificate creation
        Returns:
            ExternalCertificate: The created external certificate instance or None
        """
        if certificate_response.get("error"):
            logger.error(
                "Failed to create external certificate for user %s and course %s. certificate_response: %s",
                user,
                course_overview,
                certificate_response,
            )
            return None

        certificate_id = certificate_response.get("certificate_id", "")
        certificate_urls = certificate_response.get("certificate_urls", {})
        urls = {
            "certificate_url_en": certificate_urls.get("en", ""),
            "certificate_url_ar": certificate_urls.get("ar", ""),
        }
        external_certificate, _ = cls.objects.update_or_create(  # pylint: disable=no-member
            user=user,
            course_overview=course_overview,
            certificate_id=certificate_id,
            defaults=urls,
        )
        logger.info(
            "External certificate with ID %s created successfully for user %s and course %s.",
            certificate_id,
            user,
            course_overview,
        )

        return external_certificate
