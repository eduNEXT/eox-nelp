"""Utils that can be used for the pearson Vue integration.
"""
from django.conf import settings

from eox_nelp.pearson_vue_engine.models import PearsonEngine


def update_user_engines(user, action_type, course_id=None):
    """Update engines model using pearson vue actions.

    Args:
        user (User): User instance relation to update engine.
        action_type (str): The type of action to trigger ('rti', 'cdd', or 'ead').
        course_id (str): course_id to add update. Defaults to None.
    """
    pearson_engine, _ = PearsonEngine.objects.get_or_create(user=user)  # pylint: disable=no-member
    pearson_engine.increment_trigger(action_type)
    if course_id:
        pearson_engine.increment_course_value(course_id)


def get_user_data(user):
    """Retrieve user data for the request payload.

    Args:
        user: The user object containing user data.

    Returns:
        dict: The user data formatted for the request.
    """
    user_data = {
        "username": user.username,
        "full_name": user.profile.name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "country": user.profile.country.code,
        "city": user.profile.city,
        "phone": user.profile.phone_number,
        "address": user.profile.mailing_address,
        "arabic_full_name": user.extrainfo.arabic_name,
        "arabic_first_name": user.extrainfo.arabic_first_name,
        "arabic_last_name": user.extrainfo.arabic_last_name,
    }

    if user.extrainfo.national_id:
        user_data["national_id"] = user.extrainfo.national_id

    return user_data


def get_platform_data():
    """Retrieve platform data for the request payload.

    Returns:
        dict: The platform data formatted for the request.
    """
    return {
        "name": settings.PLATFORM_NAME,
        "tenant": getattr(settings, "EDNX_TENANT_DOMAIN", None),
    }


def generate_action_parameters(user, exam_id):
    """
    Select the appropriate parameters for the action based on the action name.

    Args:
        action_name (str): The name of the action to perform.
        user (User): the user to be processed.
        exam_id (str, optional): The ID of the exam for authorization. Default is None.
        **kwargs: Additional keyword arguments

    Returns:
        dict: The parameters for the action.
    """
    action_parameters = {
        "user_data": get_user_data(user),
        "platform_data": get_platform_data(),
        "exam_data": {"external_key": exam_id},
    }

    return action_parameters
