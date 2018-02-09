import httplib, urllib, base64

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
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

