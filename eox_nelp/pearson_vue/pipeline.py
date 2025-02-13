"""
This module contains functions that are part of a processing pipeline.

Each function in this module is designed to perform a specific step in the pipeline. The functions are intended to be
called sequentially, where each function processes data and passes it along to the next step in the pipeline.

Functions:
    get_user_data: Retrieves and processes user data.
    check_service_availability: Checks the availability of the Pearson VUE RTI service.
    import_candidate_demographics: Imports candidate demographics data.
    import_exam_authorization: Imports exam authorization data.
    get_exam_data: Retrieves exam data.
"""
import inspect
import logging

import phonenumbers
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from nelc_api_clients.clients.pearson_rti import PearsonRTIApiClient
from pydantic import ValidationError

from eox_nelp.edxapp_wrapper.certificates import generate_course_certificate
from eox_nelp.edxapp_wrapper.student import AnonymousUserId, CourseEnrollment, anonymous_id_for_user
from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD, PAYLOAD_PING_DATABASE
from eox_nelp.pearson_vue.data_classes import CddRequest, EadRequest
from eox_nelp.pearson_vue.exceptions import (
    PearsonAttributeError,
    PearsonBaseError,
    PearsonImportError,
    PearsonKeyError,
    PearsonTypeError,
    PearsonValidationError,
)
from eox_nelp.pearson_vue.utils import generate_client_authorization_id, update_xml_with_dict

try:
    from eox_audit_model.decorators import audit_method, rename_function
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x

    def rename_function(name):  # pylint: disable=unused-argument
        """Identity rename_function"""
        return lambda x: x


logger = logging.getLogger(__name__)

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
    extrainfo = getattr(user, "extrainfo", None)
    arabic_name = extrainfo.arabic_name if extrainfo else ""
    arabic_first_name = extrainfo.arabic_first_name if extrainfo else ""
    arabic_last_name = extrainfo.arabic_last_name if extrainfo else ""

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
            "arabic_first_name": arabic_first_name,
            "arabic_last_name": arabic_last_name,
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

    if response.get("status", "error") == "accepted":
        return {"cdd_import": response}

    raise PearsonImportError(
        exception_reason=f"Import candidate demographics pipeline has failed with the following response: {response}",
        pipe_frame=inspect.currentframe()
    )


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

    if response.get("status", "error") == "accepted":
        return {"ead_import": response}

    raise PearsonImportError(
        exception_reason=f"Import exam authorization pipeline has failed with the following response: {response}",
        pipe_frame=inspect.currentframe(),
    )


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
    try:
        courses_data = getattr(settings, "PEARSON_RTI_COURSES_DATA")
        exam_metadata = courses_data[course_id]
    except KeyError as exc:
        raise PearsonKeyError(exception_reason=str(exc), pipe_frame=inspect.currentframe()) from exc
    except AttributeError as a_exc:
        raise PearsonAttributeError(exception_reason=str(a_exc), pipe_frame=inspect.currentframe()) from a_exc

    # This generates the clientAuthorizationID based on the user_id and course_id
    exam_metadata["client_authorization_id"] = generate_client_authorization_id(
        User.objects.get(id=user_id),
        course_id,
    )
    # configure eligibility appt date with settings course delta starting from now. Default one year.
    elegibility_appt_delta_days = exam_metadata.get("elegibility_appt_delta_days", 365)
    exam_metadata["eligibility_appt_date_first"] = timezone.now().strftime("%Y/%m/%d %H:%M:%S")
    exam_metadata["eligibility_appt_date_last"] = (
        timezone.now() + timezone.timedelta(days=elegibility_appt_delta_days)
    ).strftime("%Y/%m/%d %H:%M:%S")

    required_fields = {
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
    try:
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
                    "firstName": profile_metadata["arabic_first_name"],
                    "lastName": profile_metadata["arabic_last_name"],
                    "address1": profile_metadata["address"],
                    "city": profile_metadata["city"],
                },
            }
        }
    except KeyError as exc:
        raise PearsonKeyError(exception_reason=str(exc), pipe_frame=inspect.currentframe()) from exc
    except AttributeError as a_exc:
        raise PearsonAttributeError(exception_reason=str(a_exc), pipe_frame=inspect.currentframe()) from a_exc

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
    try:
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
    except KeyError as exc:
        raise PearsonKeyError(exception_reason=str(exc), pipe_frame=inspect.currentframe()) from exc
    except AttributeError as a_exc:
        raise PearsonAttributeError(exception_reason=str(a_exc), pipe_frame=inspect.currentframe()) from a_exc

    return {
        "ead_request": ead_request
    }


def validate_cdd_request(cdd_request, **kwargs):  # pylint: disable=unused-argument):
    """
    Validates a CDD request dictionary using a Pydantic model.

    This function attempts to create a Pydantic model instance (likely named `class CddRequest`:
`)
    from the provided `cdd_request` dictionary. It performs data validation based on the
    model's data type definitions.
    Then if there is an error then that error is raised using audit. PearsonValidationError

    Args:
        cdd_request (dict): The dictionary containing the CDD request data.
    """
    try:
        CddRequest(**cdd_request)
    except ValidationError as exc:
        raise PearsonValidationError(exception_reason=str(exc), pipe_frame=inspect.currentframe()) from exc


def validate_ead_request(ead_request, **kwargs):  # pylint: disable=unused-argument
    """
    Validates an EAD request dictionary using a Pydantic model.

    This function attempts to create a Pydantic model instance (likely named `EadRequest`)
    from the provided `ead_request` dictionary. It performs data validation based on the
    model's data type definitions.
    Then if there is an error then that error is raised using PearsonValidationError

    Args:
        ead_request (dict): The dictionary containing the EAD request data.
    """
    try:
        EadRequest(**ead_request)
    except ValidationError as exc:
        raise PearsonValidationError(exception_reason=str(exc), pipe_frame=inspect.currentframe()) from exc


def audit_pearson_error(failed_step_pipeline="", exception_dict=None, **kwargs):  # pylint: disable=unused-argument
    """
    Method to save an error with eox-audit.
    Args:
        exception_dict(dict): dict presentation of the dict.
        failed_step_pipeline(str): Name of function of step failed.
        the audit model and the logger error.
        **kwargs
    Logs:
        LogError: log pearsonsubclass error subclass matched.
    Returns:
        None
    """
    if not exception_dict:
        return

    if not failed_step_pipeline:
        failed_step_pipeline = exception_dict.get("pipe_function")

    exception_title = ' '.join(word.capitalize() for word in exception_dict['exception_type'].split('-'))
    audit_action = f"Pearson Vue Exception: {exception_title}"

    @audit_method(action=audit_action)
    @rename_function(name=failed_step_pipeline)
    def raise_audit_pearson_exception(exception_dict, failed_step_pipeline):
        raise PearsonBaseError.from_dict(exception_dict)

    try:
        raise_audit_pearson_exception(failed_step_pipeline=failed_step_pipeline, exception_dict=exception_dict)
    except PearsonBaseError as exc:
        logger.error(exc)


def extract_result_notification_data(request_data, **kwargs):  # pylint: disable=unused-argument
    """
    Extracts result notification data from the request.

    Args:
        request_data (dict): The dictionary containing the Result Notification request data.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing extracted data including exam result, client authorization ID,
              enrollment ID, anonymous user model ID, and anonymous user ID.
    """

    try:
        client_authorization_id = request_data["authorization"]["clientAuthorizationID"]
        client_authorization_elements = client_authorization_id.split("-")
        enrollment_id = client_authorization_elements[0]
        anonymous_user_model_id = client_authorization_elements[1]
        anonymous_user_id = request_data["clientCandidateID"].replace("NELC", "")

        return {
            "exam_result": request_data["exams"]["exam"][0]["examResult"],
            "client_authorization_id": client_authorization_id,
            "enrollment_id": enrollment_id,
            "anonymous_user_model_id": anonymous_user_model_id,
            "anonymous_user_id": anonymous_user_id,
        }
    except (KeyError, IndexError) as exc:
        raise PearsonKeyError(exception_reason=str(exc), pipe_frame=inspect.currentframe()) from exc


def generate_external_certificate(enrollment=None, exam_result=None, **kwargs):  # pylint: disable=unused-argument
    """
    Generates an external certificate if the exam result meets the passing criteria.

    Args:
        enrollment (object): The enrollment object associated with the user and course.
        exam_result (dict): The dictionary containing the exam result data.
        **kwargs: Additional keyword arguments.
    """
    if not enrollment or not exam_result:
        raise PearsonTypeError(
            exception_reason="Method generate_external_certificate has failed due to a missing variable",
            pipe_frame=inspect.currentframe()
        )

    passing_score = float(exam_result.get("passingScore", 1))
    score = float(exam_result.get("score", 0))

    if score >= passing_score:
        generate_course_certificate(
            enrollment.user,
            enrollment.course_id,
            "downloadable",
            enrollment.mode,
            score,
            "batch"
        )


def get_enrollment_from_anonymous_user_id(
    anonymous_user_model_id,
    enrollment=None,
    **kwargs
):  # pylint: disable=unused-argument
    """
    Retrieves enrollment information based on the anonymous user model ID.

    Args:
        anonymous_user_model_id (str): The ID of the anonymous user model.
        enrollment (object, optional): An optional enrollment object.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the enrollment object if found, otherwise an empty dictionary.
    """
    if not enrollment:
        try:
            anonymous_user_id = AnonymousUserId.objects.get(id=anonymous_user_model_id)

            return {
                "enrollment": CourseEnrollment.objects.get(
                    user=anonymous_user_id.user,
                    course=anonymous_user_id.course_id,
                )
            }
        except ObjectDoesNotExist:
            pass

    return {}


def get_enrollment_from_id(enrollment_id, enrollment=None, **kwargs):  # pylint: disable=unused-argument
    """
    Retrieves enrollment information based on the enrollment ID.

    Args:
        enrollment_id (str): The ID of the enrollment.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the enrollment object if found, otherwise an empty dictionary.
    """
    if not enrollment:
        try:
            return {
                "enrollment": CourseEnrollment.objects.get(id=enrollment_id)
            }
        except ObjectDoesNotExist:
            pass

    return {}
