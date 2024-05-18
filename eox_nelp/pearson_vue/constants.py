"""Module to add constants related Pearson Vue Integration"""
# flake8: noqa: E501
# pylint: disable=duplicate-code

PAYLOAD_PING = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:sch="http://ws.pearsonvue.com/ping/schema">
    <soapenv:Header/>
    <soapenv:Body>
    <sch:pingServiceRequest/>
    </soapenv:Body>
</soapenv:Envelope>
"""

PAYLOAD_PING_DATABASE = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:sch="http://ws.pearsonvue.com/ping/schema">
    <soapenv:Header>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" soapenv:mustUnderstand="1">
            <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="UsernameToken-28678335">
                <wsse:Username>Username</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">Password</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <sch:pingDatabaseRequest />
    </soapenv:Body>
</soapenv:Envelope>
"""

PAYLOAD_CDD = """
<soapenv:Envelope xmlns:sch="http://ws.pearsonvue.com/rti/cdd/schema" xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
    <soapenv:Header>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" soapenv:mustUnderstand="1">
            <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="UsernameToken-26398355">
                <wsse:Username>YourUsername</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">YourPassword</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <sch:cddRequest clientCandidateID="NELC123456" clientID="YourClientID">
            <candidateName>
                <firstName>John2</firstName>
                <lastName>Smith</lastName>
                <middleName>Carl</middleName>
                <salutation>Mr</salutation>
                <suffix>Jr</suffix>
            </candidateName>
            <webAccountInfo>
                <email>abc.test@abc.com</email>
            </webAccountInfo>
            <lastUpdate>2024/04/14 09:35:18 GMT</lastUpdate>
            <primaryAddress>
                <addressType>Work</addressType>
                <companyName>Pearson VUE</companyName>
                <address1>5601 Green Valley Drive</address1>
                <address2>Suite 220</address2>
                <city>Bloomington</city>
                <state>MN</state>
                <postalCode>55437</postalCode>
                <country>USA</country>
                <phone>
                    <phoneNumber>9526813000</phoneNumber>
                    <phoneCountryCode>1</phoneCountryCode>
                </phone>
                <mobile>
                    <mobileNumber>9526813800</mobileNumber>
                    <mobileCountryCode>1</mobileCountryCode>
                </mobile>
            </primaryAddress>
            <alternateAddress>
                <addressType>Home</addressType>
                <address1>123 Main Street</address1>
                <city>Bloomington</city>
                <state>MN</state>
                <postalCode>55379</postalCode>
                <country>USA</country>
                <phone>
                    <phoneNumber>9526814311</phoneNumber>
                    <extension>1234</extension>
                    <phoneCountryCode>1</phoneCountryCode>
                </phone>
            </alternateAddress>
        </sch:cddRequest>
    </soapenv:Body>
</soapenv:Envelope>
"""
PAYLOAD_EAD = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:sch="http://ws.pearsonvue.com/rti/ead/schema">
    <soapenv:Header>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" soapenv:mustUnderstand="1">
            <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="UsernameToken-26398355">
                <wsse:Username>YourUsername</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">YourPassword</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <sch:eadRequest clientID="YourClientID" authorizationTransactionType="Add" clientAuthorizationID="A1234">
            <clientCandidateID>NELC123456</clientCandidateID>
            <examAuthorizationCount>3</examAuthorizationCount>
            <examSeriesCode>OTT</examSeriesCode>
            <eligibilityApptDateFirst>2024/05/01 00:00:00</eligibilityApptDateFirst>
            <eligibilityApptDateLast>2025/12/31 23:59:59</eligibilityApptDateLast>
            <lastUpdate>2024/05/14 23:09:01 GMT</lastUpdate>
        </sch:eadRequest>
    </soapenv:Body>
</soapenv:Envelope>
"""
from pydantic import BaseModel, Field, root_validator

class Password(BaseModel):
    type: str = Field(default='http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText', alias="@type")
    text: str = Field(alias="#text")

class UsernameToken(BaseModel):
    xmlns_wsu: str = Field(default="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd", alias="@xmlns:wsu")
    id: str = Field(default="UsernameToken-26398355", alias="@wsu:Id")
    username: str = Field(alias="wsse:Username")
    password: Password = Field(alias="wsse:Password")

class Security(BaseModel):
    xmlns_wsse: str = Field(default="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd", alias="@xmlns:wsse")
    must_understand: str = Field(default="1", alias="@soapenv:mustUnderstand")
    username_token: UsernameToken = Field(alias="wsse:UsernameToken")

class Header(BaseModel):
    security: Security = Field(alias="wsse:Security")

class Phone(BaseModel):
    phone_number: str = Field(alias="phoneNumber", max_length=20)
    phone_country_code: str = Field(alias="phoneCountryCode", max_length=3)

class Mobile(BaseModel):
    mobile_number: str = Field(alias="mobileNumber", max_length=20)
    mobile_country_code: str = Field(alias="mobileCountryCode", max_length=3)

class Address(BaseModel):
    adress_type: Optional[str] = Field(alias="addressType", default=None)
    company_name: Optional[str] = Field(alias="companyName", default=None, max_length=50)
    address1: str = Field(alias="address1", max_length=40)
    address2: Optional[str] = Field(alias="address2", default=None, max_length=40)
    city: str = Field(alias="city", max_length=32)
    state: Optional[str] = Field(alias="state", default=None, max_length=50)
    postal_code: Optional[str] = Field(alias="postalCode", default=None, max_length=16)
    country: str = Field(alias="country", max_length=3)
    phone: Optional = Field(alias="phone")
    mobile: Optional = Field(alias="mobile")

class PrimaryAddress(Address):
    pass

class AlternateAddress(Address):
    pass

class CandidateName(BaseModel):
    first_name: str = Field(alias="firstName", max_length=30)
    last_name: str = Field(alias="lastName",max_length=50)
    middle_name: Optional[str] = Field(alias="middleName", default= None, max_length=30)
    salutation: Optional[str] = Field(alias="salutation", default=None, max_length=50)
    suffix: Optional[str] = Field(alias="suffix", default=None, max_length=10)

class WebAccountInfo(BaseModel):
    email: str = Field(alias="email", max_length=255)

class CddRequest(BaseModel):
    candidate_id: Optional[str] = Field(alias="@candidateID", default=None)
    client_candidate_id: Optional[str] = Field(alias="@clientCandidateID", default=None, max_length=50)
    client_id: str = Field(alias="@clientID")
    candidate_name: CandidateName = Field(alias="candidateName")
    web_account_info: WebAccountInfo = Field(alias="webAccountInfo")
    last_update: str = Field(alias="lastUpdate")
    primary_address: PrimaryAddress = Field(alias="primaryAddress")
    alternate_address: Optional[AlternateAddress] = Field(alias="alternateAddress", default=None)

class Body(BaseModel):
    cdd_request: CddRequest = Field(alias="sch:cddRequest")

class Envelope(BaseModel):
    xmlns_sch: str = Field(default="http://ws.pearsonvue.com/rti/cdd/schema", alias="@xmlns:sch")
    xmlns_soapenv: str = Field(default="http://www.w3.org/2003/05/soap-envelope", alias="@xmlns:soapenv")
    soapenv_header: Header = Field(alias="soapenv:Header")
    soapenv_body: Body = Field(alias="soapenv:Body")


class EadRequest(BaseModel):
    client_id: str = Field(alias="@clientID")
    authorization_transaction_type: str = Field(alias="@authorizationTransactionType")
    authorization_id: Optional[str] = Field(alias="@authorizationID", default=None)
    client_authorization_id: Optional[str] = Field(alias="@clientAuthorizationID", default=None, max_length=25)
    client_candidate_id: Optional[str] = Field(alias="clientCandidateID", default=None, max_length=50)
    exam_authorization_count: str = Field(alias="examAuthorizationCount")
    exam_series_code: str = Field(alias="examSeriesCode", max_length=20)
    elegibility_appt_date_first: str = Field(alias="eligibilityApptDateFirst")
    elegibility_appt_date_last: str = Field(alias="eligibilityApptDateLast")
    last_update: str = Field(alias="lastUpdate")
