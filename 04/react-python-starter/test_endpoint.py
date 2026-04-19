import urllib.request
import json
import urllib.error

data = json.dumps({'username': 'testpy2', 'email': 'testpy2@email.com', 'password': 'abc'})
req = urllib.request.Request('http://localhost:5000/register', data=data.encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS:", response.read().decode())
except urllib.error.HTTPError as e:
    print("ERROR:", e.read().decode())
