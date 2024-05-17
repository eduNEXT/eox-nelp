"""Client module for Pearson VUE RTI service.

Classes:
    PearsonRTIApiClient: Class to interact with the pearson vue Real-Time Import external service.
"""
import logging

from bs4 import BeautifulSoup
from django.conf import settings

from eox_nelp.api_clients import AbstractSOAPClient
from eox_nelp.api_clients.authenticators import PKCS12Authenticator

try:
    from eox_audit_model.decorators import audit_method
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x


LOGGER = logging.getLogger(__name__)


class PearsonRTIApiClient(AbstractSOAPClient):
    """This class implements the required method to consume APIs available in the Pearson VUE systems
    for importing candidate demographic and exam authorization data.
    """
    authentication_class = PKCS12Authenticator

    def __init__(self):
        self.cert = getattr(settings, "PEARSON_RTI_CERT")
        self.passphrase = getattr(settings, "PEARSON_RTI_PASSPHRASE")

        super().__init__()

    @property
    def base_url(self):
        return getattr(settings, "PEARSON_RTI_WSDL_URL")

    def ping(self, payload):
        """The Ping service allows to ping the VUE system to verify that web services are available.
        This allows to validate the credentials(ping_database) if they are included into the payload.

        Arguments:
            payload<str>: Body xml request in string format.

        Returns:
            <Dict>: Parsed xml response to Dict format.
        """
        result = {
            "status": "failed",
        }
        xml_response = BeautifulSoup(
            self.make_post("cxfws2/services/Ping", payload),
            "xml",
        )
        request_result = xml_response.find("result")

        if request_result and "status" in request_result.attrs:
            result["status"] = request_result.attrs["status"]

        return result

    @audit_method(action="Import Candidate Demographics")
    def import_candidate_demographics(self, payload):
        """The CDD service imports candidate demographic data in to the VUE system. This
        method performs the required action to store the data into the Pearson service.

        Arguments:
            payload<str>: Body xml request in string format.

        Returns:
            <Dict>: Parsed xml response to Dict format.
        """
        xml_response = BeautifulSoup(
            self.make_post("cxfws2/services/CDDService", payload),
            "xml",
        )
        fault = xml_response.find("soapenv:Fault")

        # There are multiple kind of errors, some of them generates a soapenv:Fault section and others
        # generates an status error section, the following condition handles the first case.
        if fault:
            return {
                "status": "error",
                "fault_code": xml_response.find("faultcode").text,
                "message": xml_response.find("faultstring").text,
            }

        status = xml_response.find("status")

        if status:
            return {
                "status": status.text.lower(),
                "message": xml_response.find("message").text,
                "candidate_id": xml_response.find("cdd:cddResponse").attrs.get("candidateID"),
                "client_candidate_id": xml_response.find("cdd:cddResponse").attrs.get("clientCandidateID"),
            }

        LOGGER.error(
            "An unexpected error has occurred trying to make a CDD request getting the following response: %s",
            xml_response,
        )

        return {
            "status": "unexpected error",
            "response": xml_response,
        }

    @audit_method(action="Import Exam Authorization")
    def import_exam_authorization(self, payload):
        """The EAD service imports exam authorization data into the Pearson VUE system. This
        method performs the required action to store the data into the Pearson service.

        Arguments:
            payload<str>: Body xml request in string format.

        Returns:
            <Dict>: Parsed xml response to Dict format.
        """
        xml_response = BeautifulSoup(
            self.make_post("cxfws2/services/EADService", payload),
            "xml",
        )
        fault = xml_response.find("soapenv:Fault")

        # There are multiple kind of errors, some of them generates a soapenv:Fault section and others
        # generates an status error section, the following condition handles the first case.
        if fault:
            return {
                "status": "error",
                "fault_code": xml_response.find("faultcode").text,
                "message": xml_response.find("faultstring").text,
            }

        status = xml_response.find("status")

        if status:
            return {
                "status": status.text.lower(),
                "message": xml_response.find("message").text if xml_response.find("message") else "",
                "client_candidate_id": xml_response.find("clientCandidateID").text,
            }

        LOGGER.error(
            "An unexpected error has occurred trying to make a EAD request getting the following response: %s",
            xml_response,
        )

        return {
            "status": "unexpected error",
            "response": xml_response,
        }
