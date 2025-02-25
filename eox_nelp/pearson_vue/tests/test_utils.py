"""This file contains all the test for the pearson vue  utils.py file.

Classes:
    UpdatePayloadCddRequestTestCase: Tests cases for update_xml_with_dict using payload with cdd request tag cases.
    UpdatePayloadEadRequestTestCase: Test cased for update_xml_with_dict using payload with ead request tag cases.
"""
from unittest.mock import MagicMock, patch

import xmltodict
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from eox_nelp.edxapp_wrapper.student import AnonymousUserId, CourseEnrollment
from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD
from eox_nelp.pearson_vue.models import PearsonEngine
from eox_nelp.pearson_vue.utils import (
    generate_action_parameters,
    generate_client_authorization_id,
    get_platform_data,
    get_user_data,
    is_cp1252,
    update_user_engines,
    update_xml_with_dict,
)

User = get_user_model()


class UpdatePayloadCddRequestTestCase(TestCase):
    """Test case for update_xml focus on cddRequest tag with dict"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_CDD
        self.payload_base_bs = BeautifulSoup(PAYLOAD_CDD, "xml")

    def test_cdd_request_not_modified(self):
        """Test update_xml_with_dict method doesn't modify PAYLOAD_CDD
        using an empty update_dict .

        Expected behavior:
            - payload_base dict representation is the same to the payload_result dict representation.
        """
        update_dict = {}

        payload_result = update_xml_with_dict(self.payload_base, update_dict)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))

    def test_username_password_modified(self):
        """Test username and password are modified in the
          new payload string
          using update_xml_with_dict.

        Expected behavior:
            - Using payload bs representation username text is modified.
            - Using payload bs representation password text is modified.
        """
        username = "darth"
        password = "vaderpass"
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": username,
                            'wsse:Password': {
                                '#text': password
                            },
                        }
                    }
                }
            }
        }
        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertEqual(payload_result_bs.find("wsse:Username").text, username)
        self.assertEqual(payload_result_bs.find("wsse:Password").text, password)

    def test_cdd_request_modify_attrs(self):
        """Test update_xml_with_dict method modify PAYLOAD_CDD
        in the sch:cddRequest tag attributes using configure update_dict with `@` .

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - result_attrs of the new payload using bs are the same to the update dict.
        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:cddRequest": {
                        "@clientCandidateID": "newclientcandidateID",
                        "@clientID": "123999222ID",
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        result_cdd_request_attrs = payload_result_bs.find("sch:cddRequest").attrs
        for key in result_cdd_request_attrs:
            self.assertEqual(
                result_cdd_request_attrs[key],
                update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"][f"@{key}"]
            )

    def test_cdd_request_modify_candidate_name(self):
        """Test update_xml_with_dict method modify PAYLOAD_CDD
        in the candidateName tags  using update_dict.

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - text of CandidateName keys of the new payload using bs are the same to the update dict.
        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:cddRequest": {
                        "candidateName": {
                            "firstName": "Darth",
                            "lastName": "Vader",
                            "middleName": "Anakin",
                            "salutation": "Mr",
                            "suffix": "Lord",
                        }
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        for key, _ in update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["candidateName"].items():
            self.assertEqual(
                payload_result_bs.find(key).text,
                update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["candidateName"][key]
            )

    def test_cdd_request_modify_web_account_info(self):
        """Test update_xml_with_dict method modify PAYLOAD_CDD
        in the webAccountInfo tag using update_dict.

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - text of email tag of the new payload using bs is the same to the update dict.
        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:cddRequest": {
                        "webAccountInfo": {
                            "email": "vader@mail.com"
                        }
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertEqual(
            payload_result_bs.find("email").text,
            update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["webAccountInfo"]["email"]
        )

    def test_cdd_request_modify_last_update(self):
        """Test update_xml_with_dict method modify PAYLOAD_CDD
        in the lastUpdate tag  using update_dict.

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - text of email tag of the new payload using bs is the same to the update dict.
        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:cddRequest": {
                        "lastUpdate": "2033/04/14 09:35:18 GMT"
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertEqual(
            payload_result_bs.find("lastUpdate").text,
            update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["lastUpdate"]
        )

    def test_cdd_request_modify_address_info(self):
        """Test update_xml_with_dict method modify PAYLOAD_CDD
        in the primaryAddress and alternateAddress tags using update_dict.

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - primaryAddress dict-key of the new_payload_dict representation is the same to update_dict.
            - alternateAddress dict-key of the new_payload_dict representation is the same to update_dict.

        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:cddRequest": {
                        "primaryAddress": {
                            "addressType": "Work",
                            "companyName": "Pearson VUE Clark Kent",
                            "address1": "5601 Green Valley Drive",
                            "address2": "Suite 220",
                            "city": "Smallville",
                            "state": "kansas",
                            "postalCode": "55437",
                            "country": "USA",
                            "phone": {
                                "phoneNumber": "99999999",
                                "phoneCountryCode": "1"
                            },
                            "mobile": {
                                "mobileNumber": "88888888",
                                "mobileCountryCode": "1"
                            },
                            "nativeAddress": {
                                "language": "UKN",
                                "potentialMismatch": "false",
                                "firstName": "kalel",
                                "lastName": "-el",
                                "address1": "123 Antartic",
                                "city": "new york"
                            },
                        },
                        "alternateAddress": {
                            "addressType": "Home",
                            "address1": "123 Antartic",
                            "city": "Polar",
                            "state": "cold",
                            "postalCode": "55379",
                            "country": "USA",
                            "phone": {
                                "phoneNumber": "000000000",
                                "extension": "89",
                                "phoneCountryCode": "1"
                            }
                        },
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertDictEqual(
            xmltodict.parse(payload_result)["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["primaryAddress"],
            update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["primaryAddress"],
        )
        self.assertDictEqual(
            xmltodict.parse(payload_result)["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["alternateAddress"],
            update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["alternateAddress"],
        )


class UpdatePayloadEadRequestTestCase(TestCase):
    """Test case for update_xml focus on eadRequest tag with dict"""

    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_EAD
        self.payload_base_bs = BeautifulSoup(PAYLOAD_EAD, "xml")

    def test_ead_request_not_modified(self):
        """Test update_xml_with_dict method doesn't modify PAYLOAD_EAD
        using an empty update_dict .

        Expected behavior:
            - payload_base dict representation is the same to the payload_result dict representation.
        """
        update_dict = {}

        payload_result = update_xml_with_dict(self.payload_base, update_dict)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))

    def test_username_password_modified(self):
        """Test username and password are modified in the
          new payload string
          using update_xml_with_dict.

        Expected behavior:
            - Using payload bs representation username text is modified.
            - Using payload bs representation password text is modified.
        """
        username = "darth"
        password = "vaderpass"
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Header": {
                    "wsse:Security": {
                        "wsse:UsernameToken": {
                            "wsse:Username": username,
                            'wsse:Password': {
                                '#text': password
                            },
                        }
                    }
                }
            }
        }
        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertEqual(payload_result_bs.find("wsse:Username").text, username)
        self.assertEqual(payload_result_bs.find("wsse:Password").text, password)

    def test_ead_request_modify_attrs(self):
        """Test update_xml_with_dict method modify PAYLOAD_EAD
        in the sch:cddRequest tag attributes using configure update_dict with `@` .

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - result_attrs of the new payload using bs are the same to the update dict.
        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:eadRequest": {
                        "@clientID": "00000000ID",
                        "@authorizationTransactionType": "Update",
                        "@clientAuthorizationID": "A9999",
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        result_cdd_request_attrs = payload_result_bs.find("sch:eadRequest").attrs
        for key in result_cdd_request_attrs:
            self.assertEqual(
                result_cdd_request_attrs[key],
                update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:eadRequest"][f"@{key}"]
            )

    def test_ead_request_modify_all_info(self):
        """Test update_xml_with_dict method modify PAYLOAD_EAD
        in the sch:eadRequest nested tags using update_dict.

        Expected behavior:
            - payload_base dict representation is not the same to the payload_result dict representation.
            - text of CandidateName tag of the new payload using bs are the same to the update dict.
        """
        update_dict = {
            "soapenv:Envelope": {
                "soapenv:Body": {
                    "sch:eadRequest": {
                        "clientCandidateID": "Superman123456",
                        "examAuthorizationCount": "5",
                        "examSeriesCode": "OTT2",
                        "eligibilityApptDateFirst": "2024/05/01 00:00:00",
                        "eligibilityApptDateLast": "3256/12/31 23:59:59",
                        "lastUpdate": "2024/05/16 23:09:01 GMT",
                    }
                }
            }
        }

        payload_result = update_xml_with_dict(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        for key, value in update_dict["soapenv:Envelope"]["soapenv:Body"]["sch:eadRequest"].items():
            self.assertEqual(payload_result_bs.find(key).text, value)


class GenerateClientAuthorizationIDTestCase(TestCase):
    """Test case for generate_client_authorization_id."""

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user, _ = User.objects.get_or_create(
            username="Superman",
            first_name="Clark",
            last_name="Kent",
            email="superman@justiceleague.com",

        )
        self.course_id = "course-v1:Doomsday+Demo+2023"
        CourseEnrollment.objects.get.return_value = MagicMock(
            user=self.user,
            course_id=self.course_id,
            id=1,
        )
        AnonymousUserId.objects.get.return_value = MagicMock(
            user=self.user,
            course_id=self.course_id,
            id=28475,
        )

    def tearDown(self):
        """Restore mocks' state"""
        CourseEnrollment.reset_mock()
        AnonymousUserId.reset_mock()

    def test_generate_client_authorization_id(self):
        """
        Test generate_client_authorization_id function return the set values.

        Expected behavior:
            - The result is the expected value.(300001-28475)
        """
        expected_result = "1-28475"

        result = generate_client_authorization_id(self.user.id, self.course_id)

        self.assertEqual(expected_result, result)


class TestIsCp1252(TestCase):
    """Class to test is_cp1252 function"""
    def test_english_true(self):
        """Tests if a string with English characters is CP1252 encoded."""
        text = "This is a test string"

        self.assertTrue(is_cp1252(text))

    def test_arabic_false(self):
        """Tests if a string with Arabic characters is not CP1252 encoded."""
        text = "هذا هو اختبار باللغة العربية"  # Arabic text

        self.assertFalse(is_cp1252(text))

    def test_mixed_chars(self):
        """Tests if a string with mixed characters (English and Arabic) is not CP1252 encoded."""
        text = "This is a test with عربية characters"

        self.assertFalse(is_cp1252(text))

    def test_empty_string(self):
        """Tests if an empty string is considered CP1252 encoded."""
        text = ""

        self.assertTrue(is_cp1252(text))

    def test_special_chars_false(self):
        """Tests if a string with special characters is not CP1252 encoded."""
        text = "This string has ©®€ symbols"

        self.assertFalse(is_cp1252(text))


class TestUpdateUserEngineCustomForm(TestCase):
    """Class to test update_user_engines function"""
    # pylint: disable=no-member

    def test_creates_pearson_engine_if_none_exists(self):
        """Tests if a `PearsonEngine` instance is created if it doesn't exist.

        Expected Behavior:

        - If a `PearsonEngine` instance does not exist for the given user,
        a new instance should be created and associated with the user.
        """

        user = User.objects.create(username="not_exists_rti_user")

        update_user_engines(user, "cdd")

        self.assertIsInstance(user.pearsonengine, PearsonEngine)

    def test_increments_trigger_for_cdd(self):
        """Tests if the `increment_trigger` method is called and the trigger count is incremented.
        Expected Behavior:
        - The `cdd_triggers` attribute of the `PearsonEngine` instance should be incremented by 1.
        - Other colums would not be affected
        """
        initial_cdd_count = 12
        user = User.objects.create(username="incrementcdd")
        PearsonEngine.objects.create(user=user, cdd_triggers=initial_cdd_count)

        update_user_engines(user, "cdd")

        user.pearsonengine.refresh_from_db()
        self.assertEqual(user.pearsonengine.cdd_triggers, initial_cdd_count + 1)
        self.assertEqual(user.pearsonengine.ead_triggers, 0)
        self.assertEqual(user.pearsonengine.rti_triggers, 0)
        self.assertDictEqual(user.pearsonengine.courses, {})

    def test_increments_course_value_for_ead(self):
        """Tests if the `increment_course_value` method is called for "ead" actions
        and the course count is incremented.
        Expected Behavior:
        - The `rti_triggers` attribute of the `PearsonEngine` instance should be incremented by 1.
        - The course dict would be increment by one in the desired course.
        - Other colums would not be affected
        """
        initial_ead_count = 23
        course_id = "course-v1:test+awesome"
        initial_course_id_count = 99
        user = User.objects.create(username="incrementead")
        PearsonEngine.objects.create(
            user=user,
            ead_triggers=initial_ead_count,
            courses={
                course_id: initial_course_id_count
            }
        )

        update_user_engines(user, "ead", course_id)
        user.pearsonengine.refresh_from_db()

        self.assertEqual(user.pearsonengine.ead_triggers, initial_ead_count + 1)
        self.assertEqual(user.pearsonengine.cdd_triggers, 0)
        self.assertEqual(user.pearsonengine.rti_triggers, 0)
        self.assertEqual(user.pearsonengine.courses[course_id], initial_course_id_count + 1)

    def test_increments_course_value_for_rti(self):
        """Tests if the `increment_course_value` method is called for "rti" actions
        and the course count is incremented.
        Test not previous pearson engine one-one-relation instance but created.
        Expected Behavior:
        - The `rti_triggers` attribute of the `PearsonEngine` instance should be incremented by 1.
        - The course dict would be increment by one in the desired course.
        - Other colums would not be affected
        """
        user = User.objects.create(username="incrementrti")
        course_id = "course-v1:test+awesome"

        update_user_engines(user, "rti", course_id)

        user.pearsonengine.refresh_from_db()
        self.assertEqual(user.pearsonengine.rti_triggers, 1)
        self.assertEqual(user.pearsonengine.ead_triggers, 0)
        self.assertEqual(user.pearsonengine.cdd_triggers, 0)
        self.assertEqual(user.pearsonengine.courses[course_id], 1)

    def test_does_not_increment_course_value_for_other_actions(self):
        """Tests if the `increment_course_value` method is not called for other action names.
        Expected Behavior:

        - If the `action_name` is not "ead", "rti" or "cdd", raise ValueError.
        - The pearsonengine attributes should remain unchanged.
        """
        user = User.objects.create(
            username="otheactionincrement",
            pearsonengine=PearsonEngine.objects.create()
        )
        course_id = "course-v1:test+awesome"

        with self.assertRaises(ValueError):
            update_user_engines(user, "other_action", course_id)

        self.assertEqual(user.pearsonengine.cdd_triggers, 0)
        self.assertEqual(user.pearsonengine.ead_triggers, 0)
        self.assertEqual(user.pearsonengine.rti_triggers, 0)
        self.assertDictEqual(user.pearsonengine.courses, {})


class TestGetUserData(TestCase):
    """Test case for get_user_data."""

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = MagicMock(
            username="testuser",
            full_name="Test User",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            profile=MagicMock(
                country=MagicMock(code="US"),

                city="Test City",
                phone_number="123-456-7890",
                mailing_address="123 Test St",
            ),
            extrainfo=MagicMock(
                arabic_name="اسم المستخدم",
                arabic_first_name="الاسم الاول",
                arabic_last_name="اسم العائلة",
                national_id="123456789",
            )
        )

    def test_get_user_data(self):
        """
        Test get_user_data function with all user data available, including national_id.

        Expected behavior:
            - The result is a dict with all user data.
        """
        expected_result = {
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "country": self.user.profile.country.code,
            "city": self.user.profile.city,
            "phone": self.user.profile.phone_number,
            "address": self.user.profile.mailing_address,
            "arabic_full_name": self.user.extrainfo.arabic_name,
            "arabic_first_name": self.user.extrainfo.arabic_first_name,
            "arabic_last_name": self.user.extrainfo.arabic_last_name,
            "national_id": self.user.extrainfo.national_id,
        }

        result = get_user_data(self.user)

        self.assertEqual(result, expected_result)


class TestGetPlatformData(TestCase):
    """Test case for get_platform_data."""

    @override_settings(PLATFORM_NAME="Test Platform", EDNX_TENANT_DOMAIN="test.example.com")
    def test_get_platform_data_with_tenant(self):
        """
        Test get_platform_data function with PLATFORM_NAME and EDNX_TENANT_DOMAIN defined.

        Expected behavior:
            - The result is a dict with platform name and tenant domain.
        """
        expected_result = {
            "name": settings.PLATFORM_NAME,
            "tenant": settings.EDNX_TENANT_DOMAIN,
        }

        result = get_platform_data()

        self.assertEqual(result, expected_result)

    @override_settings(PLATFORM_NAME="Test Platform")
    def test_get_platform_data_without_tenant(self):
        """
        Test get_platform_data function with only PLATFORM_NAME defined.

        Expected behavior:
            - The result is a dict with platform name and tenant is None.
        """
        expected_result = {
            "name": settings.PLATFORM_NAME,
            "tenant": None,
        }

        result = get_platform_data()

        self.assertEqual(result, expected_result)


class TestGenerateActionParameters(TestCase):
    """Test case for generate_action_parameters."""

    def setUp(self):
        """
        Set up the test environment.
        """
        self.mock_get_user_data = self.patch("eox_nelp.pearson_vue.utils.get_user_data")
        self.mock_get_platform_data = self.patch("eox_nelp.pearson_vue.utils.get_platform_data")

        self.mock_get_user_data.return_value = {"user_data": "mock"}
        self.mock_get_platform_data.return_value = {"platform_data": "mock"}

    def patch(self, target, **kwargs):
        """Patch a target and return the mock"""
        patcher = patch(target, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock

    def test_generate_action_parameters(self):
        """
        Test generate_action_parameters function with exam_id.

        Expected behavior:
            - The result is a dict with user_data, platform_data, and exam_data.
            - get_user_data, get_platform_data, and get_exam_data are called once.
            - get_exam_data is called with exam_id.
        """
        user = MagicMock()
        exam_id = "exam123"

        result = generate_action_parameters(user, exam_id)

        self.assertEqual(result, {
            "user_data": {"user_data": "mock"},
            "platform_data": {"platform_data": "mock"},
            "exam_data": {"external_key": exam_id},
        })
        self.mock_get_user_data.assert_called_once_with(user)
        self.mock_get_platform_data.assert_called_once()
