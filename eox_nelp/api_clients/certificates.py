"""Client module for external certificate's API integration.

Classes:
    ExternalCertificatesApiClient: Class to interact with NELP external certificates service.
"""
from django.conf import settings

from eox_nelp.api_clients import AbstractApiClient


class ExternalCertificatesApiClient(AbstractApiClient):
    """Allow to perform multiple external certificates operations."""

    def __init__(self):
        client_id = getattr(settings, "EXTERNAL_CERTIFICATES_API_CLIENT_ID")
        client_secret = getattr(settings, "EXTERNAL_CERTIFICATES_API_CLIENT_SECRET")

        super().__init__(client_id, client_secret)

    @property
    def base_url(self):
        return getattr(settings, "EXTERNAL_CERTIFICATES_API_URL")

    def create_external_certificate(self, certificate_data):
        """This will create an external certificate based on the input data, this data should have the
        following keys:

            id <mandatory>: edx-platform certificate identifier.
            created_at <mandatory>: when the certificate was created.
            expiration_date <mandatory>: when the certificate expires.
            grade <mandatory>: The associated grade with the certificate.
            is_passing <mandatory>: Boolean value that represent if the user has passed the course.
            user <mandatory>: Dictionary with the following data:
                national_id: User National identifier.
                englishs_name <optional>: User name in English.
                arabic_name <optional>: User name in Arabic.
        Args:
            certificate_data<Dict>: Information about a the certificate.

        Returns:
            response<Dict>: requests response as dictionary.

        Raise:
            KeyError: This will be raised when the mandatory are excluded in the certificate data.
        """
        path = "certificates"  # This is not clear at all
        user = certificate_data["user"]
        payload = {
            "reference_id": certificate_data["id"],
            "date": {
                "issuance": str(certificate_data["created_at"]),
                "expiration": str(certificate_data["expiration_date"]),
            },
            "individual": {
                "name_en": user.get("english_name", ""),
                "name_ar": user.get("arabic_name", ""),
                "id": user["national_id"],
                "id_type": "saudi",
            },
            "group_code": "fail",  # This is not clear
            "certificate_type": "completion",  # What types do we have ?
            "metadata": {
                "degree": certificate_data["grade"],
                "FAIL": certificate_data["is_passing"],
            }
        }

        return self.make_post(path, payload)
