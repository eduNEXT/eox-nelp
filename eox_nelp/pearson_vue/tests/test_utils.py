"""This file contains all the test for the utils.py file.

Classes:
    ExtractCourseIdFromStringTestCase: Tests cases for the extract_course_id_from_string method.
    GetCourseFromIdTestCase: Tests cases for the get_course_from_id method.
"""
from django.test import TestCase
from eox_nelp.pearson_vue.utils import update_payload_cdd_request, update_payload_ead_request,update_payload_username_token
from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD,PAYLOAD_PING_DATABASE
from bs4 import BeautifulSoup
import xmltodict
class UpdatePayloadUsernameTokenTestCase(TestCase):
    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_PING_DATABASE
    def test_username_password_not_modified(self):
        username = "darth"
        password = "vaderpass"

        payload_result = update_payload_username_token(self.payload_base, username, password)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertEqual(payload_result_bs.find("wsse:Username").text, username)
        self.assertEqual(payload_result_bs.find("wsse:Password").text, password)

class UpdatePayloadCddRequestTestCase(TestCase):
    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_CDD
        self.payload_base_bs = BeautifulSoup(PAYLOAD_CDD, "xml")
    def test_cdd_request_not_modified(self):
        dict_mapping = {}


        payload_result = update_payload_cdd_request(self.payload_base, dict_mapping)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))

    def test_cdd_request_modify_attrs(self):
        dict_mapping = {
            "@clientCandidateID": "newclientcandidateID",
            "@clientID": "123999222ID",
        }

        payload_result = update_payload_cdd_request(self.payload_base, dict_mapping)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        result_cdd_request_attrs = payload_result_bs.find("sch:cddRequest").attrs
        for key in result_cdd_request_attrs:
            self.assertEqual(result_cdd_request_attrs[key], dict_mapping[f"@{key}"])




    def test_cdd_request_modify_candidate_name(self):
        dict_mapping = {
            "candidateName": {
                "firstName": "Darth",
                "lastName": "Vader",
                "middleName": "Anakin",
                "salutation": "Mr",
                "suffix": "Lord"
            }
        }

        payload_result = update_payload_cdd_request(self.payload_base, dict_mapping)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        for key in dict_mapping["candidateName"].keys():
            self.assertEqual(payload_result_bs.find(key).text, dict_mapping["candidateName"][key])

    def test_cdd_request_modify_web_account_info(self):
        dict_mapping = {
            "webAccountInfo": {
                "email": "vader@mail.com"
            }
        }

        payload_result = update_payload_cdd_request(self.payload_base, dict_mapping)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertEqual(payload_result_bs.find("email").text, dict_mapping["webAccountInfo"]["email"])

    def test_cdd_request_modify_last_update(self):
        dict_mapping = {
            "lastUpdate": "2033/04/14 09:35:18 GMT"
        }

        payload_result = update_payload_cdd_request(self.payload_base, dict_mapping)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertEqual(payload_result_bs.find("lastUpdate").text, dict_mapping["lastUpdate"])

    def test_cdd_request_modify_adress_info(self):
        dict_mapping = {
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
            }
        }

        payload_result = update_payload_cdd_request(self.payload_base, dict_mapping)

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertDictEqual(xmltodict.parse(payload_result)['soapenv:Envelope']['soapenv:Body']['sch:cddRequest']['primaryAddress'], dict_mapping["primaryAddress"])
        self.assertDictEqual(xmltodict.parse(payload_result)['soapenv:Envelope']['soapenv:Body']['sch:cddRequest']['alternateAddress'], dict_mapping["alternateAddress"])



class UpdatePayloadEadRequestTestCase(TestCase):
    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_EAD
        self.payload_base_bs = BeautifulSoup(PAYLOAD_EAD, "xml")

    def test_ead_request_not_modified(self):
        dict_mapping = {}

        payload_result = update_payload_ead_request(self.payload_base, dict_mapping)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))


    def test_edd_request_modify_attrs(self):
        dict_mapping = {
            "@clientID": "00000000ID",
            "@authorizationTransactionType": "Update",
            "@clientAuthorizationID":"A9999",
        }

        payload_result = update_payload_ead_request(self.payload_base, dict_mapping)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        result_cdd_request_attrs = payload_result_bs.find("sch:eadRequest").attrs
        for key in result_cdd_request_attrs:
            self.assertEqual(result_cdd_request_attrs[key], dict_mapping[f"@{key}"])

    def test_edd_request_modify_all_info(self):
        dict_mapping = {
            "clientCandidateID": "Superman123456",
            "examAuthorizationCount": "5",
            "examSeriesCode": "OTT2",
            "eligibilityApptDateFirst": "2024/05/01 00:00:00",
            "eligibilityApptDateLast": "3256/12/31 23:59:59",
            "lastUpdate": "2024/05/16 23:09:01 GMT"
        }

        payload_result = update_payload_ead_request(self.payload_base, dict_mapping)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        for key in dict_mapping.keys():
            self.assertEqual(payload_result_bs.find(key).text, dict_mapping[key])
