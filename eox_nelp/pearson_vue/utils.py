import xmltodict
def update_payload_cdd_request(payload, dict_mapping):
    payload_dict = xmltodict.parse(payload)
    payload_dict['soapenv:Envelope']['soapenv:Body']['sch:cddRequest'].update(dict_mapping)
    return xmltodict.unparse(payload_dict, full_document=False)

def update_payload_ead_request(payload, dict_mapping):
    payload_dict = xmltodict.parse(payload)
    payload_dict['soapenv:Envelope']['soapenv:Body']['sch:eadRequest'].update(dict_mapping)
    return xmltodict.unparse(payload_dict, full_document=False)

def update_payload_username_token(payload, username, password):
    payload_dict = xmltodict.parse(payload)
    payload_dict['soapenv:Envelope']['soapenv:Header']['wsse:Security']['wsse:UsernameToken']['wsse:Username'] = username
    payload_dict['soapenv:Envelope']['soapenv:Header']['wsse:Security']['wsse:UsernameToken']['wsse:Password']["#text"] = password
    return xmltodict.unparse(payload_dict, full_document=False)
