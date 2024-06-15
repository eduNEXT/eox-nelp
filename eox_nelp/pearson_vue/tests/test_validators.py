"""
This module contains unit tests for the [earson vue validators file.
"""
import unittest

from ddt import data, ddt
from pydantic.v1.utils import deep_update

from eox_nelp.pearson_vue import validators
from eox_nelp.pearson_vue.validators import validate_cdd_request, validate_ead_request


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
    )
    def test_wrong_cdd_request(self, wrong_update):
        """Test validator with a wrong cdd_request updating with empty string
        different keys.

        Expected behavior:
            - Raised  ValueError Exception
            - logs related validation error
        """
        wrong_cdd_request = deep_update(self.cdd_request, wrong_update)

        with self.assertLogs(validators.__name__, level="INFO") as logs:
            self.assertRaises(ValueError, validate_cdd_request, wrong_cdd_request)

        self.assertIn("Validation error for cdd_request", logs.output[0])

    def test_correct_cdd_request(self):
        """Test validator with correct cdd_request.

        Expected behavior:
            - expected succesful_log of good validation
        """
        client_candidate_id = self.cdd_request["@clientCandidateID"]
        succesful_log = f"Valid values for cdd_request: \n @clientCandidateID: {client_candidate_id}"

        with self.assertLogs(validators.__name__, level="INFO") as logs:
            validate_cdd_request(self.cdd_request)

        self.assertEqual(
            logs.output,
            [f"INFO:{validators.__name__}:{succesful_log}"]
        )


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
    )
    def test_wrong_ead_request(self, wrong_update):
        """Test validator with a wrong ead_request updating with empty string
        different keys.

        Expected behavior:
            - Raised  ValueError Exception
            - logs related validation error
        """
        wrong_ead_request = deep_update(self.ead_request, wrong_update)

        with self.assertLogs(validators.__name__, level="INFO") as logs:
            self.assertRaises(ValueError, validate_ead_request, wrong_ead_request)

        self.assertIn("Validation error for ead_request", logs.output[0])

    def test_correct_ead_request(self):
        """Test validator with correct ead_request.

        Expected behavior:
            - expected succesful_log of good validation
        """
        client_auth_id = self.ead_request["@clientAuthorizationID"]
        succesful_log = f"Valid values for ead_request: \n @clientAuthorizationID: {client_auth_id}"

        with self.assertLogs(validators.__name__, level="INFO") as logs:
            validate_ead_request(self.ead_request)

        self.assertEqual(
            logs.output,
            [f"INFO:{validators.__name__}:{succesful_log}"]
        )
