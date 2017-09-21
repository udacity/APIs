from httplib2 import Http
import json
import sys


print "Running Endpoint Tester....\n"
address = raw_input("Please enter the address of the server you want to access, \n If left blank the connection will be set to 'http://localhost:5000':   ")
if address == '':
	address = 'http://localhost:5000'

#GET AUTH CODE
client_url = address + "/clientOAuth"
print "Visit %s in your browser" % client_url
auth_code = ""
while auth_code == "":
	auth_code = raw_input("Paste the One-Time Auth Code Here:")

#TEST ONE GET TOKEN
try:
	h = Http()
	url = address + "/oauth/google"
	data = dict(auth_code = auth_code)
	data = json.dumps(data)
	resp, content = h.request(url, 'POST', body = data, headers = {"Content-Type": "application/json"})
	if resp['status'] != '200':
		raise Exception('Received an unsuccessful status code of %s' % resp['status'])
	new_content = json.loads(content)
	if not new_content['token']:
		raise Exception('No Token Received!')
	token = new_content['token']
except Exception as err:
	print "Test 1 FAILED: Could not exchange auth code for a token"
	print err.args
	sys.exit()
else:
	print "Test 1 PASS: Succesfully obtained token! "


#ADD TO DB WITH TOKEN

#READ FROM DB WITH TOKEN
