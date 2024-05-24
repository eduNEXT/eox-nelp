"""This file contains all the test for the pearson vue  utils.py file.

Classes:
    UpdatePayloadCddRequestTestCase: Tests cases for update_xml_with_dict using payload with cdd request tag cases.
    UpdatePayloadEadRequestTestCase: Test cased for update_xml_with_dict using payload with ead request tag cases.
"""
import xmltodict
from bs4 import BeautifulSoup
from django.test import TestCase

from eox_nelp.pearson_vue.constants import PAYLOAD_CDD, PAYLOAD_EAD
from eox_nelp.pearson_vue.utils import update_xml_with_dict


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
