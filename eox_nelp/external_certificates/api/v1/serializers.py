"""
Serializers for the external_certificates.

"""
from rest_framework import serializers

from eox_nelp.external_certificates.models import ExternalCertificate


class ExternalCertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExternalCertificate model.
    """
    user = serializers.CharField(
        source="user.id", required=False, allow_blank=True
    )
    course_overview = serializers.CharField(
        source="course_overview.id", required=False, allow_blank=True
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for the ExternalCertificateSerializer.

        Specifies the model to be serialized and the fields to be excluded from
        the serialized output.
        """
        model = ExternalCertificate
        fields = '__all__'
