"""
Module to add data_classes related Pearson Vue Integration
"""
from pydantic import AfterValidator, BaseModel, Field
from typing_extensions import Annotated

from eox_nelp.pearson_vue.utils import is_cp1252


def validate_is_cp1252(text):
    """Validate if a field is cp1252, raise exception if not.
    Anyway return the same text.

    Args:
        text (str): input to be validated

    Raises:
        ValueError: if some char is not CP1252

    Returns:
        text (str)
    """
    if not is_cp1252(text):
        raise ValueError(f"{text} -> some char is not CP1252")

    return text


Cp1252Str = Annotated[str, AfterValidator(validate_is_cp1252)]


class Phone(BaseModel):
    """Phone data class model"""
    phone_number: Cp1252Str = Field(alias="phoneNumber", min_length=1, max_length=20)
    phone_country_code: Cp1252Str = Field(alias="phoneCountryCode", min_length=1, max_length=3)


class Mobile(BaseModel):
    """Mobile data class model"""
    mobile_number: Cp1252Str = Field(alias="mobileNumber", min_length=1, max_length=20)
    mobile_country_code: Cp1252Str = Field(alias="mobileCountryCode", min_length=1, max_length=3)


class NativeAddress(BaseModel):
    """NativeAddress data class model"""
    language: str = Field(alias="language", min_length=3, max_length=3)
    potential_mismatch: str = Field(alias="potentialMismatch", min_length=1)
    first_name: str = Field(alias="firstName", min_length=1, max_length=30)
    last_name: str = Field(alias="lastName", min_length=1, max_length=50)
    address1: str = Field(alias="address1", min_length=1, max_length=40)
    city: str = Field(alias="city", min_length=1, max_length=32)


class Address(BaseModel):
    """Address data class model"""
    address1: Cp1252Str = Field(alias="address1", min_length=1, max_length=40)
    city: Cp1252Str = Field(alias="city", min_length=1, max_length=32)
    country: Cp1252Str = Field(alias="country", min_length=1, max_length=3)
    phone: Phone = Field(alias="phone")
    mobile: Mobile = Field(alias="mobile")
    native_address: NativeAddress = Field(alias="nativeAddress")


class PrimaryAddress(Address):
    """PrimaryAddress data class model"""


class AlternateAddress(Address):
    """AlternateAddress data class model"""


class CandidateName(BaseModel):
    """CandidateName data class model"""
    first_name: Cp1252Str = Field(alias="firstName", min_length=1, max_length=30)
    last_name: Cp1252Str = Field(alias="lastName", min_length=1, max_length=50)


class WebAccountInfo(BaseModel):
    """WebAccountInfo data class model"""
    email: Cp1252Str = Field(alias="email", min_length=1, max_length=255)


class CddRequest(BaseModel):
    """CddRequest data class model"""
    client_candidate_id: Cp1252Str = Field(alias="@clientCandidateID", min_length=1, max_length=50)
    client_id: Cp1252Str = Field(alias="@clientID", min_length=1)
    candidate_name: CandidateName = Field(alias="candidateName")
    last_update: Cp1252Str = Field(alias="lastUpdate", min_length=1)
    primary_address: PrimaryAddress = Field(alias="primaryAddress")
    web_account_info: WebAccountInfo = Field(alias="webAccountInfo")


class EadRequest(BaseModel):
    """EadRequest data class model"""
    client_id: Cp1252Str = Field(alias="@clientID", min_length=1)
    authorization_transaction_type: Cp1252Str = Field(alias="@authorizationTransactionType", min_length=1)
    client_authorization_id: Cp1252Str = Field(alias="@clientAuthorizationID", min_length=1, max_length=25)
    client_candidate_id: Cp1252Str = Field(alias="clientCandidateID", min_length=1, max_length=50)
    exam_authorization_count: int = Field(alias="examAuthorizationCount")
    exam_series_code: Cp1252Str = Field(alias="examSeriesCode", min_length=1, max_length=20)
    elegibility_appt_date_first: Cp1252Str = Field(alias="eligibilityApptDateFirst", min_length=1)
    elegibility_appt_date_last: Cp1252Str = Field(alias="eligibilityApptDateLast", min_length=1)
    last_update: Cp1252Str = Field(alias="lastUpdate", min_length=1)
