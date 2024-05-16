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

class UpdatePayloadEadRequestTestCase(TestCase):
    def setUp(self):
        """Setup common conditions for every test case"""
        self.payload_base = PAYLOAD_EAD
        self.payload_base_bs = BeautifulSoup(PAYLOAD_EAD, "xml")

    def test_ead_request_not_modified(self):
        dict_mapping = {}

        payload_result = update_payload_ead_request(self.payload_base, dict_mapping)

        self.assertDictEqual(xmltodict.parse(self.payload_base), xmltodict.parse(payload_result))
