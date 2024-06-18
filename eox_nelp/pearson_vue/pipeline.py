"""
This module contains functions that are part of a processing pipeline.

Each function in this module is designed to perform a specific step in the pipeline. The functions are intended to be
called sequentially, where each function processes data and passes it along to the next step in the pipeline.

Functions:
    handle_course_completion_status: Pipeline function to handle course completion status.
    get_user_data: Retrieves and processes user data.
    check_service_availability: Checks the availability of the Pearson VUE RTI service.
    import_candidate_demographics: Imports candidate demographics data.
    import_exam_authorization: Imports exam authorization data.
    get_exam_data: Retrieves exam data.
"""
import logging

import phonenumbers
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from eox_nelp.api_clients.pearson_rti import PearsonRTIApiClient
from eox_nelp.edxapp_wrapper.student import anonymous_id_for_user
from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD, PAYLOAD_PING_DATABASE
from eox_nelp.pearson_vue.utils import generate_client_authorization_id, update_xml_with_dict
from eox_nelp.signals.utils import get_completed_and_graded

logger = logging.getLogger(__name__)

User = get_user_model()


def handle_course_completion_status(user_id, course_id, **kwargs):
    """Pipeline that check the case of completion cases on the pipeline execution. Also this pipe
    has 4 behaviours depending the case:
        - skip this pipeline if setting PEARSON_RTI_TESTING_SKIP_HANDLE_COURSE_COMPLETION_STATUS is truthy.
          Pipeline continues.
        - is_passing is true means the course is graded(passed) and dont needs this pipe validation.
          The pipeline continues without changes.
        - is_complete=True and is_graded=False pipeline should continue.
          (completed courses and not graded).
        - Otherwise this indicates that the pipeline execution would be stopped,
          for grading-courses the COURSE_GRADE_NOW_PASSED signal would act.

    Args:
        user_id (int): The ID of the user whose data is to be retrieved.
        course_id (str): course_id to check completion or graded.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: Pipeline dict
    """
    if getattr(settings, "PEARSON_RTI_TESTING_SKIP_HANDLE_COURSE_COMPLETION_STATUS", False):
        logger.info(
            "Skipping `handle_course_completion_status` pipe for user_id:%s and course_id: %s",
            str(user_id),
            course_id
        )
        return None

    if kwargs.get("is_passing"):
        return None

    is_complete, is_graded = get_completed_and_graded(user_id, course_id)

    if is_complete and not is_graded:
        return None

    return {
        "safely_pipeline_termination": True,
    }


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
    extrainfo = getattr(user, "extrainfo", None)
    arabic_name = extrainfo.arabic_name if extrainfo else ""

    return {
        "profile_metadata": {
            "anonymous_user_id": anonymous_id_for_user(user, None),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "address": profile.mailing_address,
            "city": profile.city,
            "country": profile.country.alpha3,
            "phone_number": phone,
            "phone_country_code": phone_country_code,
            "mobile_number": phone,
            "mobile_country_code": phone_country_code,
            "arabic_name": arabic_name,
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


def import_candidate_demographics(cdd_request, **kwargs):  # pylint: disable=unused-argument
    """
    Imports candidate demographics data into the Pearson VUE RTI system.

    This function creates a payload with candidate demographic details and sends a request
    to the Pearson VUE RTI service to import this information. The payload includes personal
    information such as the candidate's name, email, address, phone number, and other details.
    If the import request is not accepted, the function raises an exception.

    Args:
        cdd_request(dict): cdd_request to be sent.
        **kwargs: Additional keyword arguments.

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
                "sch:cddRequest": cdd_request
            },
        },
    }
    payload = update_xml_with_dict(PAYLOAD_CDD, payload)
    response = api_client.import_candidate_demographics(payload)

    if response.get("status", "error") != "accepted":
        # pylint: disable=broad-exception-raised
        raise Exception("Error trying to process import candidate demographics request.")


def import_exam_authorization(ead_request, **kwargs):  # pylint: disable=unused-argument
    """
    Imports exam authorization data into the Pearson VUE RTI system.

    This function creates  a payload with exam  authorization details and  sends a
    request to the Pearson VUE RTI service to import this information. The payload
    includes details such as the candidate ID, exam  series code, and  eligibility
    appointment dates. If the  import request is not accepted, the function raises
    an exception.

    Args:
        ead_request(dict): ead_request to be sent.

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
                "sch:eadRequest": ead_request
            },
        },
    }
    payload = update_xml_with_dict(PAYLOAD_EAD, payload)
    response = api_client.import_exam_authorization(payload)

    if response.get("status", "error") != "accepted":
        # pylint: disable=broad-exception-raised
        raise Exception("Error trying to process import exam authorization request.")


def get_exam_data(user_id, course_id, **kwargs):  # pylint: disable=unused-argument
    """
    Retrieves exam data from Django settings.

    This function fetches the exam data from the settings using the given course ID.

    Args:
        user_id (int): Unique user identifier.
        course_id (str): Unique course identifier.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the processed user data, including:
            - eligibility_appt_date_first (str): First date an appointment can be made.
            - eligibility_appt_date_last (str): Last date an appointment can be made.
            - exam_authorization_count (str): Number of times the authorization can be consumed for registrations.
            - exam_series_code (str): Exam Series code in VUE system.
            - client_authorization_id (str): Authorization ID in the client system.

    Raises:
        Exception: If the Pearson VUE RTI service does not accept the import request.
    """
    courses_data = getattr(settings, "PEARSON_RTI_COURSES_DATA")
    exam_metadata = courses_data[course_id]

    # This generates the clientAuthorizationID based on the user_id and course_id
    exam_metadata["client_authorization_id"] = generate_client_authorization_id(
        User.objects.get(id=user_id),
        course_id,
    )

    required_fields = {
        "eligibility_appt_date_first",
        "eligibility_appt_date_last",
        "exam_authorization_count",
        "exam_series_code",
    }

    if required_fields.issubset(exam_metadata.keys()):
        return {"exam_metadata": exam_metadata}

    raise Exception(  # pylint: disable=broad-exception-raised
        (
            "Error trying to get exam data, some fields are missing for course"
            f"{course_id}. Please check PEARSON_RTI_COURSES_DATA setting."
        ),
    )


def build_cdd_request(profile_metadata, **kwargs):  # pylint: disable=unused-argument
    """Build the cdd_request dict.

    Args:
        profile_metadata (dict): Basic user data.
        **kwargs: A dictionary containing the following key-value pairs:

    Returns:
       dict: dict with ead_request dict.
    """
    cdd_request = {
        "@clientCandidateID": f'NELC{profile_metadata["anonymous_user_id"]}',
        "@clientID": getattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID"),
        "candidateName": {
            "firstName": profile_metadata["first_name"],
            "lastName": profile_metadata["last_name"],
        },
        "webAccountInfo": {
            "email": profile_metadata["email"],
        },
        "lastUpdate": timezone.now().strftime("%Y/%m/%d %H:%M:%S GMT"),
        "primaryAddress": {
            "address1": profile_metadata["address"],
            "city": profile_metadata["city"],
            "country": profile_metadata["country"],
            "phone": {
                "phoneNumber": profile_metadata["phone_number"],
                "phoneCountryCode": profile_metadata["phone_country_code"],
            },
            "mobile": {
                "mobileNumber": profile_metadata["mobile_number"],
                "mobileCountryCode": profile_metadata["mobile_country_code"],
            },
            "nativeAddress": {
                "language": getattr(settings, "PEARSON_RTI_NATIVE_ADDRESS_LANGUAGE", "UKN"),
                "potentialMismatch": "false",
                "firstName": profile_metadata["arabic_name"],
                "lastName": profile_metadata["arabic_name"],
                "address1": profile_metadata["address"],
                "city": profile_metadata["city"],
            },
        }
    }
    return {
        "cdd_request": cdd_request
    }


def build_ead_request(
    profile_metadata,
    exam_metadata,
    transaction_type="Add",
    **kwargs
):  # pylint: disable=unused-argument
    """Build the ead_request dict.

    Args:
        profile_metadata (dict): Basic user data.
        exam_metadata (dict): Exam information.
        transaction_type (str): The type of transaction for the authorization (default is "Add").
        **kwargs: A dictionary containing the following key-value pairs:

    Returns:
        dict: dict with ead_request dict
    """
    ead_request = {
        "@clientAuthorizationID": exam_metadata["client_authorization_id"],
        "@clientID": getattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID"),
        "@authorizationTransactionType": transaction_type,
        "clientCandidateID": f'NELC{profile_metadata["anonymous_user_id"]}',
        "examAuthorizationCount": exam_metadata["exam_authorization_count"],
        "examSeriesCode": exam_metadata["exam_series_code"],
        "eligibilityApptDateFirst": exam_metadata["eligibility_appt_date_first"],
        "eligibilityApptDateLast": exam_metadata["eligibility_appt_date_last"],
        "lastUpdate": timezone.now().strftime("%Y/%m/%d %H:%M:%S GMT"),
    }

    return {
        "ead_request": ead_request
    }
