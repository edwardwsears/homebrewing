import httplib, urllib, base64

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': 'f0e6ec912a504ef4bec3129aae1ce07d',
}

params = urllib.urlencode({
    'personGroupId': 'searsbeersfaces'
})

body = '{"name": "Sears Beers Faces"}'

try:
    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("PUT", "/face/v1.0/persongroups/searsbeersfaces?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

