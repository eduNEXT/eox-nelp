"""
This module contains functions that are part of a processing pipeline.

Each function in this module is designed to perform a specific step in the pipeline. The functions are intended to be
called sequentially, where each function processes data and passes it along to the next step in the pipeline.

Functions:
    get_user_data(data: dict) -> dict: Retrieves and processes user data.
"""
import phonenumbers
from django.contrib.auth import get_user_model

from eox_nelp.edxapp_wrapper.student import anonymous_id_for_user

User = get_user_model()


def get_user_data(user_id, **kwargs):  # pylint: disable=unused-argument
    """
    Retrieves and processes user data for the pipeline.

    This function fetches the user data from the database using the given user ID.
    It processes the user's profile information, including the phone number, and
    returns a dictionary with the user's anonymized ID, contact details, and other
    relevant information.

    Args:
        user_id (int): The ID of the user whose data is to be retrieved.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the processed user data, including:
            - anonymous_user_id (str): An anonymized identifier for the user.
            - username (str): The username of the user.
            - first_name (str): The first name of the user.
            - last_name (str): The last name of the user.
            - email (str): The email address of the user.
            - address (str): The mailing address of the user.
            - city (str): The city of the user's address.
            - country (str): The country code of the user's address.
            - phone_number (int): The user's phone number in national format.
            - phone_country_code (int): The country code of the user's phone number.
            - mobile_number (int): The user's mobile number in national format (same as phone_number).
            - mobile_country_code (int): The country code of the user's mobile number (same as phone_country_code).
    """
    user = User.objects.get(id=user_id)
    profile = user.profile
    phone = profile.phone_number
    pn = phonenumbers.parse(phone) if phone.startswith("+") else phonenumbers.parse(phone, profile.country.code)
    phone = str(pn.national_number)
    phone_country_code = str(pn.country_code)

    return {
        "anonymous_user_id": anonymous_id_for_user(user, None),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "address": profile.mailing_address,
        "city": profile.city,
        "country": profile.country.code,
        "phone_number": phone,
        "phone_country_code": phone_country_code,
        "mobile_number": phone,
        "mobile_country_code": phone_country_code,
    }
