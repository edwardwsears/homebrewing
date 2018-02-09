#
# This file contains functions to send/recieve
# info from the Microsoft Face API
#
#########################################
import httplib, urllib, base64
import json

header_img = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
}

header_json = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
}

params_detect = urllib.urlencode({
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender',
})

def create_person(name):

    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
    }

    body = """{
        'name': '"""+name+"""',
    }"""

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/searsbeersfaces/persons", body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    j = json.loads(data)
    return j

def delete_person(personId):

    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
    }

    params = {
        'personId': personId
    }

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("DELETE", "/face/v1.0/persongroups/searsbeersfaces/persons/%(personId)s" % params, {}, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    if (data == ""):
        return True
    else:
        return False

def list_persons():

    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
    }

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/face/v1.0/persongroups/searsbeersfaces/persons", {}, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    list_persons_json = json.loads(data)
    return list_persons_json

def detect_face(img_path):

    params_detect = urllib.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender',
    })

    try:
        #load image
        filename = img_path
        f = open(filename, "rb")
        body = f.read()
        f.close()
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        request_string = "/face/v1.0/detect?%s" % params_detect
        conn.request("POST", request_string, body, header_img)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    detect_response_json = json.loads(data)
    return detect_response_json

def add_face(img_path,personId,detect_response_json):
    params_addface = urllib.urlencode({
        # Request parameters
        'personGroupId': 'searsbeersfaces',
        'personId': personId,
        'targetFace': str(detect_response_json[0]['faceRectangle']['left'])+","+str(detect_response_json[0]['faceRectangle']['top'])+","+str(detect_response_json[0]['faceRectangle']['width'])+","+str(detect_response_json[0]['faceRectangle']['height'])
    })

    try:
        filename = img_path
        f = open(filename, "rb")
        body = f.read()
        f.close()
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/searsbeersfaces/persons/3ce71d5e-8e14-4525-897e-f4a3053c1049/persistedFaces?%s" % params_addface, body, header_img)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    addface_response_json = json.loads(data)
    return addface_response_json

def train_person_group():
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
    }

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/searsbeersfaces/train", {}, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    if (data == ""):
        return True
    else:
        return False

def get_training_status():
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '957df494c5ca4dcbbad75f45496fd38a',
    }

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/face/v1.0/persongroups/searsbeersfaces/training", {}, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    training_status_response_json = json.loads(data)
    return training_status_response_json

def identify_face(faceId):
    body = """{
        'personGroupId': 'searsbeersfaces',
        'faceIds': [
            '"""+faceId+"""',
        ],
        'maxNumOfCandidatesReturned': 1
    }"""

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        request_string = "/face/v1.0/identify"
        conn.request("POST", request_string, body, header_json)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    identify_response_json = json.loads(data)
    return identify_response_json
