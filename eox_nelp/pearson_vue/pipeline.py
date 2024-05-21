"""
This module contains functions that are part of a processing pipeline.

Each function in this module is designed to perform a specific step in the pipeline. The functions are intended to be
called sequentially, where each function processes data and passes it along to the next step in the pipeline.

Functions:
    get_user_data(data: dict) -> dict: Retrieves and processes user data.
"""
import phonenumbers
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from eox_nelp.api_clients.pearson_rti import PearsonRTIApiClient
from eox_nelp.edxapp_wrapper.student import anonymous_id_for_user

try:
    from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD, PAYLOAD_PING_DATABASE
    from eox_nelp.pearson_vue.utils import update_xml_with_dict
except ImportError:
    PAYLOAD_PING_DATABASE = None
    PAYLOAD_CDD = None
    PAYLOAD_EAD = None

    def update_xml_with_dict(x, y):  # pylint: disable=unused-argument
        """fake methiod this requires the real implementation"""
        return y

User = get_user_model()


def get_user_data(user_id, **kwargs):  # pylint: disable=unused-argument
    """
    Retrieves and processes user data for the pipeline.

    This function fetches the user data from the database using the given user ID.
    It processes the user's profile information, including the phone number, and
    returns a dictionary with the user's anonymized ID, contact details, and other
    relevant information.

    Args:
        user_id (int): The ID of the user whose data is to be retrieved.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the processed user data, including:
            - anonymous_user_id (str): An anonymized identifier for the user.
            - username (str): The username of the user.
            - first_name (str): The first name of the user.
            - last_name (str): The last name of the user.
            - email (str): The email address of the user.
            - address (str): The mailing address of the user.
            - city (str): The city of the user's address.
            - country (str): The country code of the user's address.
            - phone_number (int): The user's phone number in national format.
            - phone_country_code (int): The country code of the user's phone number.
            - mobile_number (int): The user's mobile number in national format (same as phone_number).
            - mobile_country_code (int): The country code of the user's mobile number (same as phone_country_code).
    """
    user = User.objects.get(id=user_id)
    profile = user.profile
    phone = profile.phone_number
    pn = phonenumbers.parse(phone) if phone.startswith("+") else phonenumbers.parse(phone, profile.country.code)
    phone = str(pn.national_number)
    phone_country_code = str(pn.country_code)

    return {
        "profile_metadata": {
            "anonymous_user_id": anonymous_id_for_user(user, None),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "address": profile.mailing_address,
            "city": profile.city,
            "country": profile.country.code,
            "phone_number": phone,
            "phone_country_code": phone_country_code,
            "mobile_number": phone,
            "mobile_country_code": phone_country_code,
        },
    }


def check_service_availability(**kwargs):  # pylint: disable=unused-argument
    """
    Checks the availability of the Pearson VUE RTI service by performing a ping request.

    This function creates a payload with authentication details and sends a ping request
    to the Pearson VUE RTI service to verify its availability. If the service is not
    available, it raises an exception.

    Args:
        **kwargs: Additional keyword arguments (currently not used).

    Raises:
        Exception: If the Pearson VUE RTI service is not available.
    """
    api_client = PearsonRTIApiClient()
    payload = {
        "soapenv:Envelope": {
            "soapenv:Header": {
                "wsse:Security": {
                    "wsse:UsernameToken": {
                        "wsse:Username": getattr(settings, "PEARSON_RTI_WSDL_USERNAME"),
                        "wsse:Password": {
                            "#text": getattr(settings, "PEARSON_RTI_WSDL_PASSWORD")
                        },
                    },
                },
            },
        },
    }
    payload = update_xml_with_dict(PAYLOAD_PING_DATABASE, payload)
    response = api_client.ping(payload)

    if response.get("status", "failed") == "failed":
        raise Exception("The pearson vue service is not available")  # pylint: disable=broad-exception-raised


def import_candidate_demographics(**kwargs):
    """
    Imports candidate demographics data into the Pearson VUE RTI system.

    This function creates a payload with candidate demographic details and sends a request
    to the Pearson VUE RTI service to import this information. The payload includes personal
    information such as the candidate's name, email, address, phone number, and other details.
    If the import request is not accepted, the function raises an exception.

    Args:
        **kwargs: A dictionary containing the following key-value pairs:
            - anonymous_user_id (str): An anonymized identifier for the user.
            - first_name (str): The candidate's first name.
            - last_name (str): The candidate's last name.
            - email (str): The candidate's email address.
            - address (str): The candidate's mailing address.
            - city (str): The city of the candidate's address.
            - country (str): The country code of the candidate's address.
            - phone_number (str): The candidate's phone number in national format.
            - phone_country_code (str): The country code of the candidate's phone number.
            - mobile_number (str): The candidate's mobile number in national format.
            - mobile_country_code (str): The country code of the candidate's mobile number.

    Raises:
        Exception: If the Pearson VUE RTI service does not accept the import request.
    """
    api_client = PearsonRTIApiClient()
    payload = {
        "soapenv:Envelope": {
            "soapenv:Header": {
                "wsse:Security": {
                    "wsse:UsernameToken": {
                        "wsse:Username": getattr(settings, "PEARSON_RTI_WSDL_USERNAME"),
                        "wsse:Password": {
                            "#text": getattr(settings, "PEARSON_RTI_WSDL_PASSWORD")
                        },
                    },
                },
            },
            "soapenv:Body": {
                "sch:cddRequest": {
                    "@clientCandidateID": f'NELC{kwargs["anonymous_user_id"]}',
                    "@clientID": getattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID"),
                    "candidateName": {
                        "firstName": kwargs["first_name"],
                        "lastName": kwargs["last_name"],
                    },
                    "webAccountInfo": {
                        "email": kwargs["email"],
                    },
                    "lastUpdate": timezone.now().strftime("%Y/%m/%d %H:%M:%S GMT"),
                    "primaryAddress": {
                        "address1": kwargs["address"],
                        "city": kwargs["city"],
                        "country": kwargs["country"],
                        "phone": {
                            "phoneNumber": kwargs["phone_number"],
                            "phoneCountryCode": kwargs["phone_country_code"],
                        },
                        "mobile": {
                            "mobileNumber": kwargs["mobile_number"],
                            "mobileCountryCode": kwargs["mobile_country_code"],
                        }
                    }
                },
            },
        },
    }
    payload = update_xml_with_dict(PAYLOAD_CDD, payload)
    response = api_client.import_candidate_demographics(payload)

    if response.get("status", "error") != "accepted":
        # pylint: disable=broad-exception-raised
        raise Exception("Error trying to process import candidate demographics request.")


def import_exam_authorization(transaccion_type="Add", **kwargs):
    """
    Imports exam authorization data into the Pearson VUE RTI system.

    This function creates  a payload with exam  authorization details and  sends a
    request to the Pearson VUE RTI service to import this information. The payload
    includes details such as the candidate ID, exam  series code, and  eligibility
    appointment dates. If the  import request is not accepted, the function raises
    an exception.

    Args:
        transaccion_type (str): The type of transaction for the authorization (default is "Add").
        **kwargs: A dictionary containing the following key-value pairs:
            - anonymous_user_id (str): An anonymized identifier for the user.

    Raises:
        Exception: If the Pearson VUE RTI service does not accept the import request.
    """
    api_client = PearsonRTIApiClient()
    payload = {
        "soapenv:Envelope": {
            "soapenv:Header": {
                "wsse:Security": {
                    "wsse:UsernameToken": {
                        "wsse:Username": getattr(settings, "PEARSON_RTI_WSDL_USERNAME"),
                        "wsse:Password": {
                            "#text": getattr(settings, "PEARSON_RTI_WSDL_PASSWORD")
                        },
                    },
                },
            },
            "soapenv:Body": {
                "sch:eadRequest": {
                    "@clientID": getattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID"),
                    "@authorizationTransactionType": transaccion_type,
                    "clientCandidateID": f'NELC{kwargs["anonymous_user_id"]}',
                    "examAuthorizationCount": kwargs["exam_authorization_count"],
                    "examSeriesCode": kwargs["exam_series_code"],
                    "eligibilityApptDateFirst": timezone.now().strftime("%Y/%m/%d %H:%M:%S"),
                    "eligibilityApptDateLast": (
                        timezone.now() + timezone.timedelta(days=365)
                    ).strftime("%Y/%m/%d %H:%M:%S"),
                    "lastUpdate": timezone.now().strftime("%Y/%m/%d %H:%M:%S GMT"),
                },
            },
        },
    }
    payload = update_xml_with_dict(PAYLOAD_EAD, payload)
    response = api_client.import_exam_authorization(payload)

    if response.get("status", "error") != "accepted":
        # pylint: disable=broad-exception-raised
        raise Exception("Error trying to process import exam authorization request.")
