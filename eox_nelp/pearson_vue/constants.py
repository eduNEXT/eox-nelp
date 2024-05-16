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
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token- profile-1.0#PasswordText">Password</wsse:Password>
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
