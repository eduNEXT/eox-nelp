"""Client module for external certificate's API integration.

Classes:
    ExternalCertificatesApiClient: Class to interact with NELP external certificates service.
"""
from django.conf import settings

from eox_nelp.api_clients import AbstractAPIRestClient
from eox_nelp.api_clients.authenticators import BasicAuthAuthenticator

try:
    from eox_audit_model.decorators import audit_method
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x


class ExternalCertificatesApiClient(AbstractAPIRestClient):
    """Allow to perform multiple external certificates operations."""

    authentication_class = BasicAuthAuthenticator
    extra_headers_key = "EXTERNAL_CERTIFICATES_EXTRA_HEADERS"

    def __init__(self):
        self.user = getattr(settings, "EXTERNAL_CERTIFICATES_USER")
        self.password = getattr(settings, "EXTERNAL_CERTIFICATES_PASSWORD")

        super().__init__()

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
            group_code ,mandatory>: String, this is a value provided by the client.
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
        @audit_method(action="Create External Certificate")
        def create_external_certificate_request(certificate_data):
            """This is a wrapper that allows to make audit-able the create_external_certificate method."""
            path = "Certificates"
            user = certificate_data["user"]
            payload = {
                "reference_id": certificate_data["reference_id"],
                "date": {
                    "issuance": certificate_data["created_at"],
                    "expiration": None,
                },
                "individual": {
                    "name_en": user["english_name"],
                    "name_ar": user["arabic_name"],
                    "id": user["national_id"],
                    "id_type": "saudi",
                },
                "group_code": certificate_data["group_code"],
                "certificate_type": "completion",  # What types do we have ?
                "score": {
                    "value": certificate_data["grade"],
                    "type": "percentage"
                },
                "metadata": getattr(settings, "EXTERNAL_CERTIFICATES_METADATA", {}),
            }
            return self.make_post(path, payload)

        return create_external_certificate_request(certificate_data)
