"""Utils that can be used for the pearson Vue integration.
This includes xml helpers:
    - update_xml_with_dict
"""
import xmltodict
from pydantic.v1.utils import deep_update


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
