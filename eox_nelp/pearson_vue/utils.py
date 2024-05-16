"""Utils that can be used for the pearson Vue integration"""
import xmltodict


def update_payload_cdd_request(payload, update_dict):
    """Update the `sch:cddRequest` tag using its dict representation using xmltodict
    nomenclature.
    https://github.com/martinblech/xmltodict
    https://pypi.org/project/xmltodict/

    Args:
        payload (str): str xml payload to update in the `sch:cddRequest` tag.
        update_dict (dict): Update dict representation to update xml_dict representation of payload in the
        corresponding tag.

    Returns:
        updated_payload(str): string xml representation of the updated dict representation of payload.
    """
    payload_dict = xmltodict.parse(payload)
    payload_dict["soapenv:Envelope"]["soapenv:Body"]["sch:cddRequest"].update(update_dict)
    return xmltodict.unparse(payload_dict, full_document=False)


def update_payload_ead_request(payload, update_dict):
    """Update the `sch:eadRequest` tag using its dict representation using xmltodict
    nomenclature.
    https://pypi.org/project/xmltodict/
    https://github.com/martinblech/xmltodict

    Args:
        payload (str): str xml payload to update in the `sch:eadRequest` tag.
        update_dict (dict): Update dict representation to update xml_dict representation of payload in the
        corresponding tag.

    Returns:
        updated_payload(str): string xml representation of the updated dict representation of payload.
    """
    payload_dict = xmltodict.parse(payload)
    payload_dict["soapenv:Envelope"]["soapenv:Body"]["sch:eadRequest"].update(update_dict)
    return xmltodict.unparse(payload_dict, full_document=False)


def update_payload_username_token(payload, username, password):
    """Update the `sch:eadRequest` tag using its dict representation using xmltodict
    nomenclature.
    https://pypi.org/project/xmltodict/
    https://github.com/martinblech/xmltodict

    Args:
        payload (str): str xml payload to update in the `wsse:UsernameToken` tag.
        username (str): new username to set in the `wsse:Username` tag.
        password (str): new password to set in the `wsse:Password` tag.

    Returns:
        updated_payload(str): string xml representation of the updated dict representation of payload.
    """
    payload_dict = xmltodict.parse(payload)
    payload_dict["soapenv:Envelope"]["soapenv:Header"]["wsse:Security"]["wsse:UsernameToken"][
        "wsse:Username"
    ] = username
    payload_dict["soapenv:Envelope"]["soapenv:Header"]["wsse:Security"]["wsse:UsernameToken"]["wsse:Password"][
        "#text"
    ] = password
    return xmltodict.unparse(payload_dict, full_document=False)
