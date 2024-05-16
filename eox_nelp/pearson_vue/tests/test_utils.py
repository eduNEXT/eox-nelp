"""This file contains all the test for the pearson vue  utils.py file.

Classes:
    UpdatePayloadUsernameTokenTestCase: Tests cases for update_payload_username_token method.
    UpdatePayloadCddRequestTestCase: Tests cases for update_payload_cdd_request method.
    UpdatePayloadEadRequestTestCase: Test cased for update_payload_ead_request method.
"""
import xmltodict
from bs4 import BeautifulSoup
from django.test import TestCase

from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD, PAYLOAD_PING_DATABASE
from eox_nelp.pearson_vue.utils import (
    update_payload_cdd_request,
    update_payload_ead_request,
    update_payload_username_token,
)


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
        update_dict = {}

        payload_result = update_payload_cdd_request(self.payload_base, update_dict)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))

    def test_cdd_request_modify_attrs(self):
        update_dict = {
            "@clientCandidateID": "newclientcandidateID",
            "@clientID": "123999222ID",
        }

        payload_result = update_payload_cdd_request(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        result_cdd_request_attrs = payload_result_bs.find("sch:cddRequest").attrs
        for key in result_cdd_request_attrs:
            self.assertEqual(result_cdd_request_attrs[key], update_dict[f"@{key}"])

    def test_cdd_request_modify_candidate_name(self):
        update_dict = {
            "candidateName": {
                "firstName": "Darth",
                "lastName": "Vader",
                "middleName": "Anakin",
                "salutation": "Mr",
                "suffix": "Lord",
            }
        }

        payload_result = update_payload_cdd_request(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        for key in update_dict["candidateName"].keys():
            self.assertEqual(payload_result_bs.find(key).text, update_dict["candidateName"][key])

    def test_cdd_request_modify_web_account_info(self):
        update_dict = {"webAccountInfo": {"email": "vader@mail.com"}}

        payload_result = update_payload_cdd_request(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertEqual(payload_result_bs.find("email").text, update_dict["webAccountInfo"]["email"])

    def test_cdd_request_modify_last_update(self):
        update_dict = {"lastUpdate": "2033/04/14 09:35:18 GMT"}

        payload_result = update_payload_cdd_request(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertEqual(payload_result_bs.find("lastUpdate").text, update_dict["lastUpdate"])

    def test_cdd_request_modify_adress_info(self):
        update_dict = {
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

        payload_result = update_payload_cdd_request(self.payload_base, update_dict)

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        self.assertDictEqual(
            xmltodict.parse(payload_result)["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["primaryAddress"],
            update_dict["primaryAddress"],
        )
        self.assertDictEqual(
            xmltodict.parse(payload_result)["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"]["alternateAddress"],
            update_dict["alternateAddress"],
        )


class UpdatePayloadEadRequestTestCase(TestCase):
    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_EAD
        self.payload_base_bs = BeautifulSoup(PAYLOAD_EAD, "xml")

    def test_ead_request_not_modified(self):
        update_dict = {}

        payload_result = update_payload_ead_request(self.payload_base, update_dict)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))

    def test_ead_request_modify_attrs(self):
        update_dict = {
            "@clientID": "00000000ID",
            "@authorizationTransactionType": "Update",
            "@clientAuthorizationID": "A9999",
        }

        payload_result = update_payload_ead_request(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        result_cdd_request_attrs = payload_result_bs.find("sch:eadRequest").attrs
        for key in result_cdd_request_attrs:
            self.assertEqual(result_cdd_request_attrs[key], update_dict[f"@{key}"])

    def test_ead_request_modify_all_info(self):
        update_dict = {
            "clientCandidateID": "Superman123456",
            "examAuthorizationCount": "5",
            "examSeriesCode": "OTT2",
            "eligibilityApptDateFirst": "2024/05/01 00:00:00",
            "eligibilityApptDateLast": "3256/12/31 23:59:59",
            "lastUpdate": "2024/05/16 23:09:01 GMT",
        }

        payload_result = update_payload_ead_request(self.payload_base, update_dict)
        payload_result_bs = BeautifulSoup(payload_result, "xml")

        self.assertNotEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
        for key in update_dict.keys():
            self.assertEqual(payload_result_bs.find(key).text, update_dict[key])
