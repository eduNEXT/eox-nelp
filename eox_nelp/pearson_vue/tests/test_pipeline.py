"""
This module contains unit tests for the functions in pipeline.py.
"""
# pylint: disable=too-many-lines
import unittest
from unittest.mock import MagicMock, Mock, patch

from ddt import data, ddt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from django.utils import timezone
from django_countries.fields import Country
from pydantic.v1.utils import deep_update

from eox_nelp.edxapp_wrapper.certificates import generate_course_certificate
from eox_nelp.edxapp_wrapper.student import AnonymousUserId, CourseEnrollment, anonymous_id_for_user
from eox_nelp.pearson_vue import pipeline
from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD, PAYLOAD_PING_DATABASE
from eox_nelp.pearson_vue.exceptions import (
    PearsonAttributeError,
    PearsonImportError,
    PearsonKeyError,
    PearsonTypeError,
    PearsonValidationError,
)
from eox_nelp.pearson_vue.pipeline import (
    audit_pearson_error,
    build_cdd_request,
    build_ead_request,
    check_service_availability,
    extract_result_notification_data,
    generate_external_certificate,
    get_enrollment_from_anonymous_user_id,
    get_enrollment_from_id,
    get_exam_data,
    get_user_data,
    handle_course_completion_status,
    import_candidate_demographics,
    import_exam_authorization,
    validate_cdd_request,
    validate_ead_request,
)

User = get_user_model()

CDD_REQUEST_SAMPLE = {
    "@clientCandidateID": "NELC12345",
    "@clientID": "12345678",
    "candidateName": {"firstName": "John", "lastName": "Doe"},
    "lastUpdate": "2023/05/20 12:00:00 GMT",
    "primaryAddress": {
        "address1": "123 Main St",
        "city": "Anytown",
        "country": "US",
        "mobile": {"mobileCountryCode": "1", "mobileNumber": "5551234567"},
        "nativeAddress": {
            "address1": "123 Main St",
            "city": "Anytown",
            "firstName": "كلارك",
            "language": "UKN",
            "lastName": "كينت",
            "potentialMismatch": "false",
        },
        "phone": {"phoneCountryCode": "1", "phoneNumber": "5551234567"},
    },
    "webAccountInfo": {"email": "john.doe@example.com"},
}

EAD_REQUEST_SAMPLE = {
    '@authorizationTransactionType': 'Add',
    '@clientAuthorizationID': '12345678954',
    '@clientID': '12345678',
    'clientCandidateID': 'NELC12345',
    'eligibilityApptDateFirst': '2024/07/15 11:59:59',
    'eligibilityApptDateLast': '2025/07/15 11:59:59',
    'examAuthorizationCount': 3,
    'examSeriesCode': 'ABC',
    'lastUpdate': '2023/05/20 12:00:00 GMT',
}


class TestTerminateNotFullCompletionCases(unittest.TestCase):
    """
    Unit tests for the handle_course_completion_status function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user_id = 1
        self.course_id = "course-v1:edX+213+2121"

    @override_settings(PEARSON_RTI_TESTING_SKIP_HANDLE_COURSE_COMPLETION_STATUS=True)
    @patch("eox_nelp.pearson_vue.pipeline.get_completed_and_graded")
    def test_skip_pipe_with_settings(self, get_completed_and_graded_mock):
        """Test the pipeline is skipped with truthy
        `PEARSON_RTI_TESTING_SKIP_HANDLE_COURSE_COMPLETION_STATUS` setting.
        Expected behavior:
            - logger info message expected
            - get_completed_and_graded_mock is not called.
            - Returned value is None

        """
        pipeline_kwargs = {}
        log_info = (
            f"INFO:{pipeline.__name__}:Skipping `handle_course_completion_status` "
            f"pipe for user_id:{self.user_id} and course_id: {self.course_id}"
        )

        with self.assertLogs(pipeline.__name__, level="INFO") as logs:
            result = handle_course_completion_status(self.user_id, self.course_id, **pipeline_kwargs)

        self.assertEqual(logs.output, [log_info])
        get_completed_and_graded_mock.assert_not_called()
        self.assertIsNone(result)

    @patch("eox_nelp.pearson_vue.pipeline.get_completed_and_graded")
    def test_check_is_passing_bypass(self, get_completed_and_graded_mock):
        """Test the pipeline dont do anything if is_passing kwarg is truthy.
        Expected behavior:
            - get_completed_and_graded_mock is not called.
            - Returned value is None

        """
        pipeline_kwargs = {"is_passing": True}

        result = handle_course_completion_status(self.user_id, self.course_id, **pipeline_kwargs)

        get_completed_and_graded_mock.assert_not_called()
        self.assertIsNone(result)

    @patch("eox_nelp.pearson_vue.pipeline.get_completed_and_graded")
    def test_check_is_complete_not_graded(self, get_completed_and_graded_mock):
        """Test the pipeline return expected dict with empty `is_passing`, and
           is_complete=True, is_graded=False.
        Expected behavior:
            - Returned value is None

        """
        pipeline_kwargs = {}
        get_complete_and_graded_output = {
            "is_complete": True,
            "is_graded": False,
        }
        get_completed_and_graded_mock.return_value = (
            get_complete_and_graded_output["is_complete"],
            get_complete_and_graded_output["is_graded"],
        )

        result = handle_course_completion_status(self.user_id, self.course_id, **pipeline_kwargs)

        self.assertIsNone(result)

    @patch("eox_nelp.pearson_vue.pipeline.get_completed_and_graded")
    def test_check_not_complete_not_graded(self, get_completed_and_graded_mock):
        """Test the pipeline return expected dict(safely_pipeline_termination) with empty `is_passing`, and
           is_complete=False, is_graded=False.
        Expected behavior:
            - Returned value is dict with `safely_pipeline_termination`
        """
        pipeline_kwargs = {}
        get_complete_and_graded_output = {
            "is_complete": False,
            "is_graded": False,
        }
        expected_output = {
            "safely_pipeline_termination": True,
        }
        get_completed_and_graded_mock.return_value = (
            get_complete_and_graded_output["is_complete"],
            get_complete_and_graded_output["is_graded"],
        )

        result = handle_course_completion_status(self.user_id, self.course_id, **pipeline_kwargs)

        self.assertDictEqual(expected_output, result)

    @patch("eox_nelp.pearson_vue.pipeline.get_completed_and_graded")
    def test_check_not_complete_graded(self, get_completed_and_graded_mock):
        """Test the pipeline return expected dict(safely_pipeline_termination) with empty `is_passing`, and
           is_complete=False, is_graded=True.
        Expected behavior:
            - Returned value is dict with `safely_pipeline_termination`
        """
        pipeline_kwargs = {}
        get_complete_and_graded_output = {
            "is_complete": False,
            "is_graded": True,
        }
        expected_output = {
            "safely_pipeline_termination": True,
        }
        get_completed_and_graded_mock.return_value = (
            get_complete_and_graded_output["is_complete"],
            get_complete_and_graded_output["is_graded"],
        )

        result = handle_course_completion_status(self.user_id, self.course_id, **pipeline_kwargs)

        self.assertDictEqual(expected_output, result)

    @patch("eox_nelp.pearson_vue.pipeline.get_completed_and_graded")
    def test_check_complete_graded(self, get_completed_and_graded_mock):
        """Test the pipeline return expected dict(safely_pipeline_termination) with empty `is_passing`, and
           is_complete=True, is_graded=True.
        Expected behavior:
            - Returned value is dict with `safely_pipeline_termination`
        """
        pipeline_kwargs = {}
        get_complete_and_graded_output = {
            "is_complete": True,
            "is_graded": True,
        }
        expected_output = {
            "safely_pipeline_termination": True,
        }
        get_completed_and_graded_mock.return_value = (
            get_complete_and_graded_output["is_complete"],
            get_complete_and_graded_output["is_graded"],
        )

        result = handle_course_completion_status(self.user_id, self.course_id, **pipeline_kwargs)

        self.assertDictEqual(expected_output, result)


@ddt
class TestGetUserData(unittest.TestCase):
    """
    Unit tests for the get_user_data function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user, _ = User.objects.get_or_create(
            username="Gamekeeper2024",
            first_name="Rubeus",
            last_name="Hagrid",
            email="rubeus.hagrid@hogwarts.com",

        )
        self.profile = MagicMock(
            mailing_address="Abbey Road 25",
            city="London",
            country=Country("GB"),

        )
        self.extrainfo = MagicMock(
            arabic_name="كلارك كينت",
            arabic_first_name="كلارك",
            arabic_last_name="كينت",
        )
        anonymous_id_for_user.return_value = "ABCDF1245678899"
        setattr(User, "profile", self.profile)
        setattr(User, "extrainfo", self.extrainfo)

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        anonymous_id_for_user.reset_mock()
        delattr(User, "extrainfo")

    @data("+443214567895", "3214567895")
    def test_get_user_data(self, phone):
        """
        Test get_user_data , this checks that the response is the expected when the
        phone_number has and doesn't have the country code.

            Expected behavior:
            - The result is as the expected output.
        """
        phone_number = phone[3:] if phone.startswith("+") else phone
        country_code = "44"  # This is the code for GB
        self.profile.phone_number = phone

        expected_output = {
            "profile_metadata": {
                "anonymous_user_id": anonymous_id_for_user(self.user, None),
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "address": self.profile.mailing_address,
                "city": self.profile.city,
                "country": self.profile.country.alpha3,
                "phone_number": phone_number,
                "phone_country_code": country_code,
                "mobile_number": phone_number,
                "mobile_country_code": country_code,
                "arabic_name": self.extrainfo.arabic_name,
                "arabic_first_name": self.extrainfo.arabic_first_name,
                "arabic_last_name": self.extrainfo.arabic_last_name,
            },
        }
        result = get_user_data(self.user.id)

        self.assertEqual(result, expected_output)


class TestCheckServiceAvailability(unittest.TestCase):
    """
    Unit tests for the check_service_availability function.
    """

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_check_service_availability_success(self, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the check_service_availability function succeeds when the service is available.

            Expected behavior:
            - PearsonRTIApiClient initialization was called once.
            - update_xml_with_dict was called with the right parameters.
            - ping method was called with the result of update_xml_with_dict.
        """
        expected_payload = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": settings.PEARSON_RTI_WSDL_USERNAME,
                            "wsse:Password": {
                                "#text": settings.PEARSON_RTI_WSDL_PASSWORD
                            },
                        },
                    },
                },
            },
        }
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.ping.return_value = {"status": "success"}

        check_service_availability()

        mock_api_client.assert_called_once()
        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_PING_DATABASE, expected_payload)
        mock_api_client.return_value.ping.assert_called_once_with(mock_update_xml_with_dict())

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_check_service_availability_failure(self, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the check_service_availability function raises an exception when the service is not available.

            Expected behavior:
            - Function raises an exception.
            - Exception message is the expected.
            - update_xml_with_dict was called with the right parameters.
            - ping method was called with the result of update_xml_with_dict.
        """
        expected_payload = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": settings.PEARSON_RTI_WSDL_USERNAME,
                            "wsse:Password": {
                                "#text": settings.PEARSON_RTI_WSDL_PASSWORD
                            },
                        },
                    },
                },
            },
        }
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.ping.return_value = {"status": "failed"}

        with self.assertRaises(Exception) as context:
            check_service_availability()

        self.assertEqual(str(context.exception), "The pearson vue service is not available")
        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_PING_DATABASE, expected_payload)
        mock_api_client.return_value.ping.assert_called_once_with(mock_update_xml_with_dict())


class TestImportCandidateDemographics(unittest.TestCase):
    """
    Unit tests for the import_candidate_demographics function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.cdd_request = CDD_REQUEST_SAMPLE

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_import_candidate_demographics_success(self, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the import_candidate_demographics function succeeds when the import request is accepted.

            Expected behavior:
            - update_xml_with_dict was called with the right parameters.
            - import_candidate_demographics method was called with the result of update_xml_with_dict.
        """
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.import_candidate_demographics.return_value = {"status": "accepted"}
        input_data = {
            "cdd_request": self.cdd_request
        }
        expected_payload = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": settings.PEARSON_RTI_WSDL_USERNAME,
                            "wsse:Password": {
                                "#text": settings.PEARSON_RTI_WSDL_PASSWORD
                            },
                        },
                    },
                },
                "soapenv:Body": {
                    "sch:cddRequest": self.cdd_request
                },
            },
        }

        import_candidate_demographics(**input_data)

        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_CDD, expected_payload)
        mock_api_client.return_value.import_candidate_demographics.assert_called_once_with(mock_update_xml_with_dict())

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_import_candidate_demographics_failure(self, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the import_candidate_demographics function raises an exception
        when the import request is not accepted.

            Expected behavior:
            - Function raises a PearsonImportError exception.
            - Exception message is the expected.
            - update_xml_with_dict was called with the right parameters.
            - import_candidate_demographics method was called with the result of update_xml_with_dict.
        """
        mock_update_xml_with_dict.return_value = 'updated_payload'
        response_return = {"status": "error"}
        mock_api_client.return_value.import_candidate_demographics.return_value = response_return
        input_data = {
            "cdd_request": self.cdd_request
        }
        expected_payload = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": settings.PEARSON_RTI_WSDL_USERNAME,
                            "wsse:Password": {
                                "#text": settings.PEARSON_RTI_WSDL_PASSWORD
                            },
                        },
                    },
                },
                "soapenv:Body": {
                    "sch:cddRequest": self.cdd_request
                },
            },
        }

        with self.assertRaises(PearsonImportError) as context:
            import_candidate_demographics(**input_data)

        self.assertEqual(
            context.exception.exception_reason,
            f"Import candidate demographics pipeline has failed with the following response: {response_return}"
        )
        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_CDD, expected_payload)
        mock_api_client.return_value.import_candidate_demographics.assert_called_once_with(mock_update_xml_with_dict())


class TestImportExamAuthorization(unittest.TestCase):
    """
    Unit tests for the import_exam_authorization function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.ead_request = EAD_REQUEST_SAMPLE

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_import_exam_authorization_success(self, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the import_exam_authorization function succeeds when the import request is accepted.

            Expected behavior:
            - update_xml_with_dict was called with the right parameters.
            - import_exam_authorization method was called with the result of update_xml_with_dict.
        """
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.import_exam_authorization.return_value = {"status": "accepted"}
        input_data = {
            "ead_request": self.ead_request
        }
        expected_payload = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": settings.PEARSON_RTI_WSDL_USERNAME,
                            "wsse:Password": {
                                "#text": settings.PEARSON_RTI_WSDL_PASSWORD
                            },
                        },
                    },
                },
                "soapenv:Body": {
                    "sch:eadRequest": self.ead_request
                },
            },
        }

        import_exam_authorization(**input_data)

        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_EAD, expected_payload)
        mock_api_client.return_value.import_exam_authorization.assert_called_once_with(mock_update_xml_with_dict())

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_import_exam_authorization_failure(self, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the import_exam_authorization function raises an exception when the import request is not accepted.

            Expected behavior:
            - Function raises a PearsonImportError exception.
            - Exception message is the expected.
            - update_xml_with_dict was called with the right parameters.
            - import_exam_authorization method was called with the result of update_xml_with_dict.
        """
        mock_update_xml_with_dict.return_value = 'updated_payload'
        response_return = {"status": "error"}
        mock_api_client.return_value.import_exam_authorization.return_value = response_return
        input_data = {
            "ead_request": self.ead_request
        }
        expected_payload = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": settings.PEARSON_RTI_WSDL_USERNAME,
                            "wsse:Password": {
                                "#text": settings.PEARSON_RTI_WSDL_PASSWORD
                            },
                        },
                    },
                },
                "soapenv:Body": {
                    "sch:eadRequest": self.ead_request
                },
            },
        }

        with self.assertRaises(PearsonImportError) as context:
            import_exam_authorization(**input_data)

        self.assertEqual(
            context.exception.exception_reason,
            f"Import exam authorization pipeline has failed with the following response: {response_return}",
        )
        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_EAD, expected_payload)
        mock_api_client.return_value.import_exam_authorization.assert_called_once_with(mock_update_xml_with_dict())


class TestGetExamData(unittest.TestCase):
    """
    Unit tests for the get_exam_data function.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user, _ = User.objects.get_or_create(
            username="Gamekeeper2024",
            first_name="Rubeus",
            last_name="Hagrid",
            email="rubeus.hagrid@hogwarts.com",

        )
        self.course_id = "course-v1:FutureX+guide+2023"
        CourseEnrollment.objects.get.return_value = MagicMock(
            user=self.user,
            id=1,
            course_id=self.course_id
        )

    def tearDown(self):
        """Restore mocks' state"""
        CourseEnrollment.reset_mock()

    @patch.object(timezone, "now")
    @override_settings()
    def test_get_exam_data_success(self, mock_now):
        """
        Test that the get_exam_data function return the set values.

            Expected behavior:
            - The result is the expected value.
        """
        mock_now.return_value = timezone.datetime(2024, 5, 20, 12, 0, 0)
        course_id = self.course_id
        exam_data = {
            "exam_authorization_count": 3,
            "exam_series_code": "ABD",
        }
        course_settings = {
            course_id: exam_data
        }
        setattr(settings, "PEARSON_RTI_COURSES_DATA", course_settings)
        expected_data = {
            **exam_data,
            "eligibility_appt_date_first": mock_now().strftime("%Y/%m/%d %H:%M:%S"),
            "eligibility_appt_date_last": (mock_now() + timezone.timedelta(days=365)).strftime("%Y/%m/%d %H:%M:%S"),
        }

        result = get_exam_data(self.user.id, course_id)
        for key, value in expected_data.items():
            self.assertEqual(result["exam_metadata"][key], value)

    @override_settings()
    def test_get_exam_data_failure(self):
        """
        Test that the get_exam_data function raises an exception when the required settings are not found.

            Expected behavior:
            - Function raises an exception.
            - Exception message is the expected.
        """
        course_id = self.course_id
        course_settings = {
            course_id: {
                "invalid_key": "test",
                "exam_authorization_count": 4,
            }
        }
        setattr(settings, "PEARSON_RTI_COURSES_DATA", course_settings)

        with self.assertRaises(Exception) as context:
            get_exam_data(self.user.id, course_id)

        self.assertEqual(
            str(context.exception),
            (
                "Error trying to get exam data, some fields are missing for course"
                f"{course_id}. Please check PEARSON_RTI_COURSES_DATA setting."
            ),
        )

    @override_settings()
    def test_wrong_exam_metadata_key_error(self):
        """ Test that the get_exam_data function raises an exception when the required settings are not found.
            Expected behavior:
            - Raise Pearson Vue key error.
        """
        setattr(settings, "PEARSON_RTI_COURSES_DATA", {})

        self.assertRaises(PearsonKeyError, get_exam_data, self.user.id, self.course_id)

    @override_settings()
    def test_wrong_exam_metadata_attr_error(self):
        """ Test that the get_exam_data function raises an exception when the required settings are not found.
            Expected behavior:
            - Raise Pearson Vue attribute error.
        """
        if hasattr(settings, "PEARSON_RTI_COURSES_DATA"):
            delattr(settings, "PEARSON_RTI_COURSES_DATA")

        self.assertRaises(PearsonAttributeError, get_exam_data, self.user.id, self.course_id)


class TestBuildCddRequest(unittest.TestCase):
    """
    Unit tests for the build_cdd_request function.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        self.input_data = {
            "profile_metadata": {
                "anonymous_user_id": "12345",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "address": "123 Main St",
                "city": "Anytown",
                "country": "US",
                "phone_number": "5551234567",
                "phone_country_code": "1",
                "mobile_number": "5551234567",
                "mobile_country_code": "1",
                "arabic_name": "فلان الفلاني",
                "arabic_first_name": "كلارك",
                "arabic_last_name": "كينت",
            }
        }

    @patch("eox_nelp.pearson_vue.pipeline.timezone")
    def test_cdd_request(self, mock_timezone):
        """ Test cdd_request is built with profile_metadata.
            Expected behavior:
            - The result is the expected value.
        """
        mock_timezone.now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)

        expected_output = {
            "cdd_request": CDD_REQUEST_SAMPLE
        }

        result = build_cdd_request(**self.input_data)
        self.assertDictEqual(expected_output, result)

    @patch("eox_nelp.pearson_vue.pipeline.timezone")
    def test_wrong_cdd_request_key_error(self, mock_timezone):
        """ Test cdd_request is not built with profile_metadata.
            Expected behavior:
            - Raise Pearson Vue key error.
        """
        mock_timezone.now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        self.input_data["profile_metadata"] = {}

        self.assertRaises(PearsonKeyError, build_cdd_request, **self.input_data)

    @override_settings()
    @patch("eox_nelp.pearson_vue.pipeline.timezone")
    def test_wrong_cdd_request_attr_error(self, mock_timezone):
        """ Test cdd_request is not built with profile_metadata.
            Expected behavior:
            - Raise Pearson Vue Attribute error.
        """
        mock_timezone.now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        if hasattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID"):
            delattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID")

        self.assertRaises(PearsonAttributeError, build_cdd_request, **self.input_data)


class TestBuildEadRequest(unittest.TestCase):
    """
    Unit tests for the build_cdd_request function.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        self.input_data = {
            "profile_metadata": {
                "anonymous_user_id": "12345",
            },
            "exam_metadata": {
                "eligibility_appt_date_first": "2024/07/15 11:59:59",
                "eligibility_appt_date_last": "2025/07/15 11:59:59",
                "exam_authorization_count": 3,
                "exam_series_code": "ABC",
                "client_authorization_id": "12345678954",
            },
        }

    @patch.object(timezone, "now")
    def test_build_ead_request(self, mock_now):
        """ Test ead_request is built with profile_metadata and exam_metadata.
            Expected behavior:
            - The result is the expected value.
        """
        mock_now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)

        expected_output = {
            "ead_request": EAD_REQUEST_SAMPLE
        }

        result = build_ead_request(**self.input_data)

        self.assertDictEqual(expected_output, result)

    @patch.object(timezone, "now")
    def test_wrong_build_ead_request_key(self, mock_now):
        """ Test ead_request is not built with profile_metadata and exam_metadata.
            Expected behavior:
            - Raise Pearson Vue key error.
        """
        mock_now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)

        self.input_data["profile_metadata"] = {}

        self.assertRaises(PearsonKeyError, build_ead_request, **self.input_data)

    @override_settings()
    @patch.object(timezone, "now")
    def test_wrong_build_ead_request_attr_error(self, mock_now):
        """ Test ead_request is not built with profile_metadata and exam_metadata.
            Expected behavior:
            - Raise Pearson Vue attribute error.
        """
        mock_now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        if hasattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID"):
            delattr(settings, "PEARSON_RTI_WSDL_CLIENT_ID")

        self.assertRaises(PearsonAttributeError, build_ead_request, **self.input_data)


@ddt
class TestValidateCddRequest(unittest.TestCase):
    """
    Unit tests for the validate_cdd_request method.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.cdd_request = {
            "@clientCandidateID": "NELC12345",
            "@clientID": "12345678",
            "candidateName": {"firstName": "John", "lastName": "Doe"},
            "lastUpdate": "2023/05/20 12:00:00 GMT",
            "primaryAddress": {
                "address1": "123 Main St",
                "city": "Anytown",
                "country": "US",
                "mobile": {"mobileCountryCode": "1", "mobileNumber": "5551234567"},
                "nativeAddress": {
                    "address1": "123 Main St",
                    "city": "Anytown",
                    "firstName": "فلان الفلاني",
                    "language": "UKN",
                    "lastName": "فلان الفلاني",
                    "potentialMismatch": "false",
                },
                "phone": {"phoneCountryCode": "1", "phoneNumber": "5551234567"},
            },
            "webAccountInfo": {"email": "john.doe@example.com"},
        }

    @data(
        {"@clientCandidateID": ""},
        {"@clientID": ""},
        {"candidateName": {"firstName": ""}},
        {"candidateName": {"lastName": ""}},
        {"lastUpdate": ""},
        {"primaryAddress": {"address1": ""}},
        {"primaryAddress": {"city": ""}},
        {"primaryAddress": {"country": ""}},
        {"primaryAddress": {"mobile": {"mobileCountryCode": ""}}},
        {"primaryAddress": {"mobile": {"mobileNumber": ""}}},
        {"primaryAddress": {"nativeAddress": {"address1": ""}}},
        {"primaryAddress": {"nativeAddress": {"city": ""}}},
        {"primaryAddress": {"nativeAddress": {"firstName": ""}}},
        {"primaryAddress": {"nativeAddress": {"language": ""}}},
        {"primaryAddress": {"nativeAddress": {"lastName": ""}}},
        {"primaryAddress": {"nativeAddress": {"potentialMismatch": ""}}},
        {"primaryAddress": {"phone": {"phoneCountryCode": ""}}},
        {"primaryAddress": {"phone": {"phoneNumber": ""}}},
        {"webAccountInfo": {"email": ""}},
        {"@clientCandidateID": "فلان"},
        {"@clientID": "فلان"},
        {"candidateName": {"firstName": "فلان"}},
        {"candidateName": {"lastName": "فلان"}},
        {"lastUpdate": "فلان"},
        {"primaryAddress": {"address1": "فلان"}},
        {"primaryAddress": {"city": "فلان"}},
        {"primaryAddress": {"country": "فلان"}},
        {"primaryAddress": {"mobile": {"mobileCountryCode": "فلان"}}},
        {"primaryAddress": {"mobile": {"mobileNumber": "فلان"}}},
        {"primaryAddress": {"phone": {"phoneCountryCode": "فلان"}}},
        {"primaryAddress": {"phone": {"phoneNumber": "فلان"}}},
        {"webAccountInfo": {"email": "فلان"}},
    )
    def test_wrong_cdd_request(self, wrong_update):
        """Test validator with a wrong cdd_request updating with empty string
        different keys.

        Expected behavior:
            - raise PearsonValidationError
        """
        wrong_cdd_request = deep_update(self.cdd_request, wrong_update)

        self.assertRaises(PearsonValidationError, validate_cdd_request, wrong_cdd_request)

    def test_correct_cdd_request(self):
        """Test validator with correct cdd_request.

        Expected behavior:
            - The result is the expected value.
        """
        self.assertIsNone(validate_cdd_request(self.cdd_request))


@ddt
class TestValidateEadRequest(unittest.TestCase):
    """
    Unit tests for the validate_ead_request method.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.ead_request = {
            '@authorizationTransactionType': 'Add',
            '@clientAuthorizationID': '12345678954',
            '@clientID': '12345678',
            'clientCandidateID': 'NELC12345',
            'eligibilityApptDateFirst': '2024/07/15 11:59:59',
            'eligibilityApptDateLast': '2025/07/15 11:59:59',
            'examAuthorizationCount': 3,
            'examSeriesCode': 'ABC',
            'lastUpdate': '2023/05/20 12:00:00 GMT',
        }

    @data(
        {"@authorizationTransactionType": ""},
        {"@clientAuthorizationID": ""},
        {"@clientID": ""},
        {"clientCandidateID": ""},
        {"eligibilityApptDateFirst": ""},
        {"eligibilityApptDateLast": ""},
        {"examAuthorizationCount": ""},
        {"examSeriesCode": ""},
        {"lastUpdate": ""},
        {"@authorizationTransactionType": "فلان"},
        {"@clientAuthorizationID": "فلان"},
        {"@clientID": "فلان"},
        {"clientCandidateID": "فلان"},
        {"eligibilityApptDateFirst": "فلان"},
        {"eligibilityApptDateLast": "فلان"},
        {"examAuthorizationCount": "فلان"},
        {"examSeriesCode": "فلان"},
        {"lastUpdate": "فلان"},
    )
    def test_wrong_ead_request(self, wrong_update):
        """Test validator with a wrong ead_request updating with empty string
        different keys.

        Expected behavior:
            - raise PearsonValidationError
        """
        wrong_ead_request = deep_update(self.ead_request, wrong_update)

        self.assertRaises(PearsonValidationError, validate_ead_request, wrong_ead_request)

    def test_correct_ead_request(self):
        """Test validator with correct ead_request.

        Expected behavior:
            - The result is the expected value.
        """
        self.assertIsNone(validate_ead_request(self.ead_request))


class TestAuditPipeError(unittest.TestCase):
    """
    Unit tests for the audit_pearson_error method.
    """

    def test_audit_pearson_error(self):
        """Test correct behaviour calling  audit_pearson_error.

        Expected behavior:
            - The result is the expected value(None).
            - Expected log error.
        """
        kwargs = {
            'exception_dict': {
                'exception_type': 'validation-error',
                'exception_reason': "error: ['String to short.']",
                'pipe_args_dict': {
                    "cdd_request": {}
                },
                'pipe_function': 'validate_cdd_request',
            },
            "failed_step_pipeline": 'validate_cdd_request',
        }

        log_error = [
            f"ERROR:{pipeline.__name__}:{str(kwargs['exception_dict'])}"

        ]

        with self.assertLogs(pipeline.__name__, level="ERROR") as logs:
            self.assertIsNone(audit_pearson_error(**kwargs))
        self.assertListEqual(log_error, logs.output)

    @patch("eox_nelp.pearson_vue.pipeline.logger")
    def test_not_audit_pearson_error(self, logger_mock):
        """Test not  behaviour calling  audit_pearson_error.
        If kwargs doesnt have `exception_data`.

        Expected behavior:
            - The result is the expected value(None).
            - Not expected log error.
        """
        kwargs = {
            'exception_dict': {},
            "failed_step_pipeline": None,
        }

        self.assertIsNone(audit_pearson_error(**kwargs))
        logger_mock.error.assert_not_called()


@ddt
class TestExtractResultNotificationData(unittest.TestCase):
    """
    Unit tests for the extract_result_notification_data function.
    """

    def test_extract_result_notification_data_success(self):
        """Test correct extraction of result notification data.

        Expected behavior:
            - The returned dictionary contains the correct extracted data.
        """
        request_data = {
            "authorization": {"clientAuthorizationID": "1234-5678"},
            "clientCandidateID": "NELC9012",
            "exams": {"exam": [{"examResult": "Pass"}]}
        }
        expected_result = {
            "exam_result": "Pass",
            "client_authorization_id": "1234-5678",
            "enrollment_id": "1234",
            "anonymous_user_model_id": "5678",
            "anonymous_user_id": "9012",
        }

        result = extract_result_notification_data(request_data)
        self.assertEqual(result, expected_result)

    @data(
        ({"clientCandidateID": "NELC9012", "exams": {"exam": [{"examResult": "Pass"}]}}),
        ({"authorization": {"clientAuthorizationID": "12-58"}, "exams": {"exam": [{"examResult": "Pass"}]}}),
        ({"authorization": {"clientAuthorizationID": "12-5"}, "clientCandidateID": "NELC2", "exams": {"exam": []}}),
    )
    def test_extract_result_notification_data_missing_data(self, request_data):
        """Test extraction with missing required data fields.

        Expected behavior:
            - The specified exception is raised due to missing data.
        """
        with self.assertRaises(PearsonKeyError):
            extract_result_notification_data(request_data)


@ddt
class TestGenerateExternalCertificate(unittest.TestCase):
    """
    Unit tests for the generate_external_certificate function.
    """

    def tearDown(self):
        """Reset the mock after each test."""
        generate_course_certificate.reset_mock()

    @data(
        ({'passingScore': '50', 'score': '75'}),
        ({'passingScore': '0', 'score': '0'}),
    )
    def test_generate_external_certificate_success(self, exam_result):
        """Test generating an external certificate when the score meets the passing criteria.

        Expected behavior:
            - The generate_course_certificate function is called with the correct arguments.
        """
        enrollment = Mock(user='test_user', course_id='test_course', mode='test_mode')

        generate_external_certificate(enrollment, exam_result)

        generate_course_certificate.assert_called_once_with(
            'test_user', 'test_course', 'downloadable', 'test_mode', float(exam_result["score"]), 'batch'
        )

    @data(
        ({'passingScore': '50', 'score': '25'}),
        ({'passingScore': '100', 'score': '99'}),
    )
    def test_generate_external_certificate_various_scores(self, exam_result):
        """Test generating an external certificate with various scores.

        Expected behavior:
            - The generate_course_certificate function is not called.
        """
        enrollment = Mock(user='test_user', course_id='test_course', mode='test_mode')

        generate_external_certificate(enrollment, exam_result)

        generate_course_certificate.assert_not_called()

    def test_generate_external_certificate_invalid_arguments(self):
        """Test generating an external certificate with invalid arguments.

        Expected behavior:
            - The specified exception is raised due to invalid data.
        """
        with self.assertRaises(PearsonTypeError):
            generate_external_certificate(enrollment=None, exam_result=None)


class TestGetEnrollmentFromAnonymousUserId(unittest.TestCase):
    """
    Unit tests for the get_enrollment_from_anonymous_user_id function.
    """

    def tearDown(self):
        """
        Reset the mocked objects after each test.
        """
        CourseEnrollment.reset_mock()
        AnonymousUserId.reset_mock()
        AnonymousUserId.objects.get.side_effect = None

    def test_get_enrollment_found(self):
        """
        Test retrieval of enrollment information when the anonymous user ID is found.

        Expected behavior:
            - The function returns a dictionary containing the enrollment object.
            - Verify that the correct calls are made to retrieve the anonymous user and enrollment objects.
        """
        anonymous_user_model_id = "valid_id"
        anonymous_user_id = Mock(user='test_user', course_id='test_course')
        course_enrollment_obj = Mock()
        AnonymousUserId.objects.get.return_value = anonymous_user_id
        CourseEnrollment.objects.get.return_value = course_enrollment_obj

        result = get_enrollment_from_anonymous_user_id(anonymous_user_model_id)

        self.assertEqual(result, {"enrollment": course_enrollment_obj})
        AnonymousUserId.objects.get.assert_called_once_with(id=anonymous_user_model_id)
        CourseEnrollment.objects.get.assert_called_once_with(
            user=anonymous_user_id.user,
            course=anonymous_user_id.course_id,
        )

    def test_get_enrollment_not_found(self):
        """
        Test behavior when the anonymous user ID is not found.

        Expected behavior:
            - The function returns an empty dictionary.
            - Verify that the call to retrieve the anonymous user object raises ObjectDoesNotExist.
            - Ensure that no attempt is made to retrieve the enrollment object.
        """
        anonymous_user_model_id = "invalid_id"
        AnonymousUserId.objects.get.side_effect = ObjectDoesNotExist

        result = get_enrollment_from_anonymous_user_id(anonymous_user_model_id)

        self.assertEqual(result, {})
        AnonymousUserId.objects.get.assert_called_once_with(id=anonymous_user_model_id)
        CourseEnrollment.objects.get.assert_not_called()

    def test_get_enrollment_with_provided_enrollment(self):
        """
        Test behavior when an enrollment object is provided as an argument.

        Expected behavior:
            - The function returns a dictionary containing an empty object.
            - Verify that no calls are made to retrieve objects from the database.
        """
        # Call the function under test with an enrollment object
        result = get_enrollment_from_anonymous_user_id("valid_id", enrollment=Mock())

        # Assert the result
        self.assertEqual(result, {})

        # Verify mock calls
        AnonymousUserId.objects.get.assert_not_called()
        CourseEnrollment.objects.get.assert_not_called()


class TestGetEnrollmentFromId(unittest.TestCase):
    """
    Unit tests for the get_enrollment_from_id function.
    """

    def tearDown(self):
        """
        Reset the mocked objects after each test.
        """
        CourseEnrollment.reset_mock()
        CourseEnrollment.objects.get.side_effect = None

    def test_get_enrollment_found(self):
        """
        Test retrieval of enrollment information when the enrollment ID is found.

        Expected behavior:
            - The function returns a dictionary containing the enrollment object.
            - Verify that the correct call is made to retrieve the enrollment object.
        """
        enrollment_id = "valid_id"
        enrollment_obj = Mock()
        CourseEnrollment.objects.get.return_value = enrollment_obj

        result = get_enrollment_from_id(enrollment_id)

        self.assertEqual(result, {"enrollment": enrollment_obj})
        CourseEnrollment.objects.get.assert_called_once_with(id=enrollment_id)

    def test_get_enrollment_not_found(self):
        """
        Test behavior when the enrollment ID is not found.

        Expected behavior:
            - The function returns an empty dictionary.
            - Verify that the call to retrieve the enrollment object raises ObjectDoesNotExist.
        """
        enrollment_id = "invalid_id"
        CourseEnrollment.objects.get.side_effect = ObjectDoesNotExist

        result = get_enrollment_from_id(enrollment_id)

        self.assertEqual(result, {})
        CourseEnrollment.objects.get.assert_called_once_with(id=enrollment_id)

    def test_get_enrollment_with_provided_enrollment(self):
        """
        Test behavior when an enrollment object is provided as an argument.

        Expected behavior:
            - The function returns a dictionary containing an empty object.
            - Verify that no calls are made to retrieve objects from the database.
        """
        # Call the function under test with an enrollment object
        result = get_enrollment_from_id("valid_id", enrollment=Mock())

        # Assert the result
        self.assertEqual(result, {})

        # Verify mock calls
        CourseEnrollment.objects.get.assert_not_called()
