"""Module to add constants related Pearson Vue Integration"""
# flake8: noqa: E501
# pylint: disable=duplicate-code

RESULT_NOTIFICATION = "result-notification"
PLACE_HOLD = "place-hold"
RELEASE_HOLD = "release-hold"
MODIFY_RESULT_STATUS = "modify-result-status"
REVOKE_RESULT = "revoke-result"
UNREVOKE_RESULT = "unrevoke-result"

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
                <wsse:Username></wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"></wsse:Password>
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
                <wsse:Username></wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"></wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <sch:cddRequest clientCandidateID="" clientID="">
            <candidateName>
                <firstName></firstName>
                <lastName></lastName>
            </candidateName>
            <webAccountInfo>
                <email></email>
            </webAccountInfo>
            <lastUpdate></lastUpdate>
            <primaryAddress>
                <address1></address1>
                <city></city>
                <country></country>
                <phone>
                    <phoneNumber></phoneNumber>
                    <phoneCountryCode></phoneCountryCode>
                </phone>
                <mobile>
                    <mobileNumber></mobileNumber>
                    <mobileCountryCode></mobileCountryCode>
                </mobile>
                <nativeAddress>
                    <language></language>
                    <potentialMismatch></potentialMismatch>
                    <firstName></firstName>
                    <lastName></lastName>
                    <address1></address1>
                    <city></city>
                </nativeAddress>
            </primaryAddress>
        </sch:cddRequest>
    </soapenv:Body>
</soapenv:Envelope>
"""
PAYLOAD_EAD = """
<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope" xmlns:sch="http://ws.pearsonvue.com/rti/ead/schema">
    <soapenv:Header>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" soapenv:mustUnderstand="1">
            <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="UsernameToken-26398355">
                <wsse:Username></wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"></wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <sch:eadRequest clientID="" authorizationTransactionType="" clientAuthorizationID="" >
            <clientCandidateID></clientCandidateID>
            <examAuthorizationCount></examAuthorizationCount>
            <examSeriesCode></examSeriesCode>
            <eligibilityApptDateFirst></eligibilityApptDateFirst>
            <eligibilityApptDateLast></eligibilityApptDateLast>
            <lastUpdate></lastUpdate>
        </sch:eadRequest>
    </soapenv:Body>
</soapenv:Envelope>
"""
