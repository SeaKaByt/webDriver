import requests

# Define the endpoint URL
url = 'http://aqctpuat1.hphit.hutchisonports.com:38550/services/message/adsiService'

# Define headers
headers = {'Content-Type': 'application/xml'}

# Define the XML payload
xml_payload = '''<?xml version="1.0" encoding="UTF-8"?>
<RSIU>
   <tid>0092</tid>
   <datetime>20230308083132</datetime>
   <id>RSIU</id>
   <block>YEG</block>
   <stack>1</stack>
   <lane>0</lane>
   <code>00000008</code>
   <remark>1,99999,9999999999999999</remark>
</RSIU>'''

# Define credentials
username = 'oscar'
password = '!auto12345'

# Send the POST request with Basic Authentication
try:
    response = requests.post(url, data=xml_payload, headers=headers, auth=(username, password), timeout=10)
    response.raise_for_status()
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)
except requests.exceptions.RequestException as e:
    print("Error:", e)