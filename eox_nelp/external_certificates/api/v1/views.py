"""
Views for external certificates API.

This module provides API endpoints for managing and validating external certificates.

Available Views:
- upsert_external_certificate: Create or update an external certificate based on the provided certificate response data.
"""
from django.contrib.auth import get_user_model
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.permissions import JwtHasScope
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.external_certificates.api.v1.serializers import (
    ExternalCertificateSerializer,
    UpsertExternalCertificateSerializer,
)
from eox_nelp.external_certificates.models import ExternalCertificate

User = get_user_model()


class UpsertExternalCertificateView(APIView):
    """Class to upsert external certificates"""
    authentication_classes = [JwtAuthentication]
    permission_classes = [JwtHasScope]
    required_scopes = ["external_certificates:write"]

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """Upsert external certificate.
        Create or update an external certificate based on the provided certificate response data.
        Also associate the certificate with the corresponding user and result notification.

        ## Usage
        ### **POST** eox-nelp/api/external-certificates/v1/upsert/
        **Request Body Example**
        ```json
        {
            "user_id": "2",
            "course_id": "course-v1:test+CS304+2025_T3",
            "certificate_response": {
                "message": "Certificate created successfully",
                "certificate_id": "TEST25YO59VV76QL",
                "certificate_urls": {
                    "en": "https://ce.nelc.gov.sa/storage/pdf/OTT-lms/TEST25YO59VV76QL-en-1740573557.pdf",
                    "ar": "https://ce.nelc.gov.sa/storage/pdf/OTT-lms/TEST25YO59VV76QL-ar-1740573555.pdf"
                }
            }
        }
        ```
        **Response Example**
        ```json
        {
            "user": "1",
            "course_overview": "course-v1:test+CS304+2025_T3",
            "certificate_id": "TEST25YO59VV76QL",
            "certificate_url_en": "https://ce.nelc.gov.sa/storage/pdf/OTT-lms/TEST25YO59VV76QL-en-1740573557.pdf",
            "certificate_url_ar": "https://ce.nelc.gov.sa/storage/pdf/OTT-lms/TEST25YO59VV76QL-ar-1740573555.pdf",
            "created_at": "2025-02-26T23:25:02.364189Z"
        }
        ```
        """
        upsert_data_serializer = UpsertExternalCertificateSerializer(data=request.data)
        if not upsert_data_serializer.is_valid():
            return Response(
                {"errors": upsert_data_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(id=request.data["user_id"])
            course_overview = CourseOverview.objects.get(id=request.data["course_id"])
            external_certificate = ExternalCertificate.create_external_certificate_from_certificate_response(
                certificate_response=request.data["certificate_response"],
                user=user,
                course_overview=course_overview,
            )
        except User.DoesNotExist:
            return Response(
                {
                    "error": f'user_id={request.data["user_id"]} User object with that id doesnt exists'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except CourseOverview.DoesNotExist:
            return Response(
                {
                    "error": f'course_id={request.data["course_id"]} CourseOverview object with that id doesnt exists'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ExternalCertificateSerializer(external_certificate).data,
            status=status.HTTP_201_CREATED,
        )
