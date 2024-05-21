"""
This module contains unit tests for the functions in pipeline.py.
"""
import unittest
from unittest.mock import MagicMock, patch

from ddt import data, ddt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_countries.fields import Country

from eox_nelp.edxapp_wrapper.student import anonymous_id_for_user
from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD, PAYLOAD_PING_DATABASE
from eox_nelp.pearson_vue.pipeline import (
    check_service_availability,
    get_user_data,
    import_candidate_demographics,
    import_exam_authorization,
)

User = get_user_model()


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
        anonymous_id_for_user.return_value = "ABCDF1245678899"
        setattr(User, "profile", self.profile)

    def tearDown(self):  # pylint: disable=invalid-name
        """Reset mocks"""
        anonymous_id_for_user.reset_mock()

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

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    @patch("eox_nelp.pearson_vue.pipeline.timezone")
    def test_import_candidate_demographics_success(self, mock_timezone, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the import_candidate_demographics function succeeds when the import request is accepted.

            Expected behavior:
            - update_xml_with_dict was called with the right parameters.
            - import_candidate_demographics method was called with the result of update_xml_with_dict.
        """
        mock_timezone.now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.import_candidate_demographics.return_value = {"status": "accepted"}
        input_data = {
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
            },
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
                    "sch:cddRequest": {
                        "@clientCandidateID": f'NELC{input_data["profile_metadata"]["anonymous_user_id"]}',
                        "@clientID": settings.PEARSON_RTI_WSDL_CLIENT_ID,
                        "candidateName": {
                            "firstName": input_data["profile_metadata"]["first_name"],
                            "lastName": input_data["profile_metadata"]["last_name"],
                        },
                        "webAccountInfo": {
                            "email": input_data["profile_metadata"]["email"],
                        },
                        "lastUpdate": mock_timezone.now().strftime("%Y/%m/%d %H:%M:%S GMT"),
                        "primaryAddress": {
                            "address1": input_data["profile_metadata"]["address"],
                            "city": input_data["profile_metadata"]["city"],
                            "country": input_data["profile_metadata"]["country"],
                            "phone": {
                                "phoneNumber": input_data["profile_metadata"]["phone_number"],
                                "phoneCountryCode": input_data["profile_metadata"]["phone_country_code"],
                            },
                            "mobile": {
                                "mobileNumber": input_data["profile_metadata"]["mobile_number"],
                                "mobileCountryCode": input_data["profile_metadata"]["mobile_country_code"],
                            }
                        }
                    },
                },
            },
        }

        import_candidate_demographics(**input_data)

        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_CDD, expected_payload)
        mock_api_client.return_value.import_candidate_demographics.assert_called_once_with(mock_update_xml_with_dict())

    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    @patch("eox_nelp.pearson_vue.pipeline.timezone")
    def test_import_candidate_demographics_failure(self, mock_timezone, mock_update_xml_with_dict, mock_api_client):
        """
        Test that the import_candidate_demographics function raises an exception
        when the import request is not accepted.

            Expected behavior:
            - Function raises an exception.
            - Exception message is the expected.
            - update_xml_with_dict was called with the right parameters.
            - import_candidate_demographics method was called with the result of update_xml_with_dict.
        """
        mock_timezone.now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.import_candidate_demographics.return_value = {"status": "error"}
        input_data = {
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
            },
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
                    "sch:cddRequest": {
                        "@clientCandidateID": f'NELC{input_data["profile_metadata"]["anonymous_user_id"]}',
                        "@clientID": settings.PEARSON_RTI_WSDL_CLIENT_ID,
                        "candidateName": {
                            "firstName": input_data["profile_metadata"]["first_name"],
                            "lastName": input_data["profile_metadata"]["last_name"],
                        },
                        "webAccountInfo": {
                            "email": input_data["profile_metadata"]["email"],
                        },
                        "lastUpdate": mock_timezone.now().strftime("%Y/%m/%d %H:%M:%S GMT"),
                        "primaryAddress": {
                            "address1": input_data["profile_metadata"]["address"],
                            "city": input_data["profile_metadata"]["city"],
                            "country": input_data["profile_metadata"]["country"],
                            "phone": {
                                "phoneNumber": input_data["profile_metadata"]["phone_number"],
                                "phoneCountryCode": input_data["profile_metadata"]["phone_country_code"],
                            },
                            "mobile": {
                                "mobileNumber": input_data["profile_metadata"]["mobile_number"],
                                "mobileCountryCode": input_data["profile_metadata"]["mobile_country_code"],
                            }
                        }
                    },
                },
            },
        }

        with self.assertRaises(Exception) as context:
            import_candidate_demographics(**input_data)

        self.assertEqual(str(context.exception), "Error trying to process import candidate demographics request.")
        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_CDD, expected_payload)
        mock_api_client.return_value.import_candidate_demographics.assert_called_once_with(mock_update_xml_with_dict())


class TestImportExamAuthorization(unittest.TestCase):
    """
    Unit tests for the import_exam_authorization function.
    """

    @patch.object(timezone, "now")
    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_import_exam_authorization_success(self, mock_update_xml_with_dict, mock_api_client, mock_now):
        """
        Test that the import_exam_authorization function succeeds when the import request is accepted.

            Expected behavior:
            - update_xml_with_dict was called with the right parameters.
            - import_exam_authorization method was called with the result of update_xml_with_dict.
        """
        mock_now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.import_exam_authorization.return_value = {"status": "accepted"}
        input_data = {
            "profile_metadata": {
                "anonymous_user_id": "12345",
            },
            "exam_metadata": {
                "exam_authorization_count": 3,
                "exam_series_code": "ABC",
            },
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
                    "sch:eadRequest": {
                        "@clientID": settings.PEARSON_RTI_WSDL_CLIENT_ID,
                        "@authorizationTransactionType": "Add",
                        "clientCandidateID": f'NELC{input_data["profile_metadata"]["anonymous_user_id"]}',
                        "examAuthorizationCount": input_data["exam_metadata"]["exam_authorization_count"],
                        "examSeriesCode": input_data["exam_metadata"]["exam_series_code"],
                        "eligibilityApptDateFirst": mock_now().strftime("%Y/%m/%d %H:%M:%S"),
                        "eligibilityApptDateLast": (
                            mock_now() + timezone.timedelta(days=365)
                        ).strftime("%Y/%m/%d %H:%M:%S"),
                        "lastUpdate": mock_now().strftime("%Y/%m/%d %H:%M:%S GMT"),
                    },
                },
            },
        }

        import_exam_authorization(**input_data)

        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_EAD, expected_payload)
        mock_api_client.return_value.import_exam_authorization.assert_called_once_with(mock_update_xml_with_dict())

    @patch.object(timezone, "now")
    @patch("eox_nelp.pearson_vue.pipeline.PearsonRTIApiClient")
    @patch("eox_nelp.pearson_vue.pipeline.update_xml_with_dict")
    def test_import_exam_authorization_failure(self, mock_update_xml_with_dict, mock_api_client, mock_now):
        """
        Test that the import_exam_authorization function raises an exception when the import request is not accepted.

            Expected behavior:
            - Function raises an exception.
            - Exception message is the expected.
            - update_xml_with_dict was called with the right parameters.
            - import_exam_authorization method was called with the result of update_xml_with_dict.
        """
        mock_now.return_value = timezone.datetime(2023, 5, 20, 12, 0, 0)
        mock_update_xml_with_dict.return_value = 'updated_payload'
        mock_api_client.return_value.import_exam_authorization.return_value = {"status": "error"}
        input_data = {
            "profile_metadata": {
                "anonymous_user_id": "12345",
            },
            "exam_metadata": {
                "exam_authorization_count": 3,
                "exam_series_code": "ABC",
            },
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
                    "sch:eadRequest": {
                        "@clientID": settings.PEARSON_RTI_WSDL_CLIENT_ID,
                        "@authorizationTransactionType": "Add",
                        "clientCandidateID": f'NELC{input_data["profile_metadata"]["anonymous_user_id"]}',
                        "examAuthorizationCount": input_data["exam_metadata"]["exam_authorization_count"],
                        "examSeriesCode": input_data["exam_metadata"]["exam_series_code"],
                        "eligibilityApptDateFirst": mock_now().strftime("%Y/%m/%d %H:%M:%S"),
                        "eligibilityApptDateLast": (
                            mock_now() + timezone.timedelta(days=365)
                        ).strftime("%Y/%m/%d %H:%M:%S"),
                        "lastUpdate": mock_now().strftime("%Y/%m/%d %H:%M:%S GMT"),
                    },
                },
            },
        }

        with self.assertRaises(Exception) as context:
            import_exam_authorization(**input_data)

        self.assertEqual(str(context.exception), "Error trying to process import exam authorization request.")
        mock_update_xml_with_dict.assert_called_once_with(PAYLOAD_EAD, expected_payload)
        mock_api_client.return_value.import_exam_authorization.assert_called_once_with(mock_update_xml_with_dict())
