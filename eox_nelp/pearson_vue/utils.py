"""Utils that can be used for the pearson Vue integration.
This includes xml helpers:
    - update_xml_with_dict
"""
import xmltodict
from pydantic.v1.utils import deep_update

from eox_nelp.edxapp_wrapper.student import AnonymousUserId, CourseEnrollment, anonymous_id_for_user
from eox_nelp.pearson_vue.constants import CLIENT_AUTHORIZATION_ID_OFFSET


def update_xml_with_dict(xml: str, update_dict: dict) -> str:
    """Update an xml string using its dict representation, deep_update,
    and auxiliar update_dict using xmltodict
    nomenclature: (keys~tags, values~text, attrs~@keys).
    https://github.com/martinblech/xmltodict
    https://pypi.org/project/xmltodict/
    To update the dict is used deep_update method of pydantic.https://docs.pydantic.dev/latest/
    https://github.com/pydantic/pydantic/blob/15b82a90c9f20db0ce618caffe6b4cb3c05ba139/pydantic/v1/utils.py#L213

    Args:
        xml (str): str xml payload to update.
        update_dict (dict): Update_dict representation to update xml_dict representation in the
        corresponding tags.

    Returns:
        updated_xml(str): string xml representation of the updated_dict representation.
    """
    xml_dict = xmltodict.parse(xml)
    result = deep_update(xml_dict, update_dict)
    return xmltodict.unparse(result, full_document=False)


def generate_client_authorization_id(user_id: int, course_id: str) -> str:
    """Use course_enrollment_id to generate client_authorization_id for EAD requests.
    Args:
        user_id (int): user id
        course_id (str): course id
    Returns:
        str: string that represents the client_auth_id
    """
    course_enrollment = CourseEnrollment.objects.get(user_id=user_id, course_id=course_id)
    anonymous_user_id = anonymous_id_for_user(course_enrollment.user, course_id)
    anonymous_user_id_instance = AnonymousUserId.objects.get(anonymous_user_id=anonymous_user_id)

    return f"{course_enrollment.id + CLIENT_AUTHORIZATION_ID_OFFSET}-{anonymous_user_id_instance.id}"
