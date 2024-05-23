"""
Module to add data_classes related Pearson Vue Integration
"""
# pylint: disable=missing-class-docstring
from pydantic import BaseModel, Field


class Phone(BaseModel):
    phone_number: str = Field(alias="phoneNumber", min_length=1, max_length=20)
    phone_country_code: str = Field(alias="phoneCountryCode", min_length=1, max_length=3)


class Mobile(BaseModel):
    mobile_number: str = Field(alias="mobileNumber", min_length=1, max_length=20)
    mobile_country_code: str = Field(alias="mobileCountryCode", min_length=1, max_length=3)


class NativeAddress(BaseModel):
    language: str = Field(alias="language", min_length=3, max_length=3)
    potential_mismatch: str = Field(alias="potentialMismatch", min_length=1)
    first_name: str = Field(alias="firstName", min_length=1, max_length=30)
    last_name: str = Field(alias="lastName", min_length=1, max_length=50)
    address1: str = Field(alias="address1", min_length=1, max_length=40)
    city: str = Field(alias="city", min_length=1, max_length=32)


class Address(BaseModel):
    address1: str = Field(alias="address1", min_length=1, max_length=40)
    city: str = Field(alias="city", min_length=1, max_length=32)
    country: str = Field(alias="country", min_length=1, max_length=3)
    phone: Phone = Field(alias="phone")
    mobile: Mobile = Field(alias="mobile")
    native_address: NativeAddress = Field(alias="nativeAddress")


class PrimaryAddress(Address):
    pass


class AlternateAddress(Address):
    pass


class CandidateName(BaseModel):
    first_name: str = Field(alias="firstName", min_length=1, max_length=30)
    last_name: str = Field(alias="lastName", min_length=1, max_length=50)


class WebAccountInfo(BaseModel):
    email: str = Field(alias="email", min_length=1, max_length=255)


class CddRequest(BaseModel):
    client_candidate_id: str = Field(alias="@clientCandidateID", min_length=1, max_length=50)
    client_id: str = Field(alias="@clientID", min_length=1)
    candidate_name: CandidateName = Field(alias="candidateName")
    last_update: str = Field(alias="lastUpdate", min_length=1)
    primary_address: PrimaryAddress = Field(alias="primaryAddress")
    web_account_info: WebAccountInfo = Field(alias="webAccountInfo")


class EadRequest(BaseModel):
    client_id: str = Field(alias="@clientID", min_length=1)
    authorization_transaction_type: str = Field(alias="@authorizationTransactionType", min_length=1)
    client_authorization_id: str = Field(alias="@clientAuthorizationID", min_length=1, max_length=25)
    client_candidate_id: str = Field(alias="clientCandidateID", min_length=1, max_length=50)
    exam_authorization_count: int = Field(alias="examAuthorizationCount")
    exam_series_code: str = Field(alias="examSeriesCode", min_length=1, max_length=20)
    elegibility_appt_date_first: str = Field(alias="eligibilityApptDateFirst", min_length=1)
    elegibility_appt_date_last: str = Field(alias="eligibilityApptDateLast", min_length=1)
    last_update: str = Field(alias="lastUpdate", min_length=1)
