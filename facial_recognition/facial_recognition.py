import face_api
from picamera import PiCamera
from time import sleep
import requests
import threading


FACE_STATE_PENDING          = 0
FACE_STATE_RECOGNIZED       = 1
FACE_STATE_NOT_REGISTERED   = 2
FACE_STATE_NO_FACE          = 3

face_state = ""
face_username = ""
face_age = 0
face_gender = ""

# Facial recognition api query thread
class facial_recognition_thread(threading.Thread):
    def __init__(self,camera,facialRecognitionPending):
        threading.Thread.__init__(self)
        self.camera = camera
        self.facialRecognitionPending = facialRecognitionPending
    def run(self):
        facial_recognition(self.camera,self.facialRecognitionPending)

# Creates facial recognition thread and runs it
def start_facial_recognition_thread(camera,facialRecognitionPending):
    if (threading.activeCount() == 1):
        thread = facial_recognition_thread(camera,facialRecognitionPending)
        thread.start()
    else:
        print "Thread still running, ignoring request"

# Facial Recognition main function
#
# Takes picture and uses face_api.py to recognize face.
# Updates searsbeers.com db for last pour stats
#
def facial_recognition(camera,facialRecognitionPending):

    facialRecognitionPending.set()

    #camera.annotate_text = "Hey there big boi"
    img_file = "/home/pi/homebrewing/facial_recognition/face_imgs/identify_img.jpg"
    camera.start_preview()
    sleep(2)
    camera.capture(img_file)
    camera.stop_preview()

    detect_response_json = face_api.detect_face(img_file)

    if (len(detect_response_json) == 0):
        # no faces detected
        print "No Faces Detected"
        set_face_stats(FACE_STATE_NO_FACE,"",0,"");
        facialRecognitionPending.clear()
        return

    identify_response_json = face_api.identify_face(detect_response_json[0]['faceId'])
    list_persons_json = face_api.list_persons()

    if (len(identify_response_json[0]['candidates']) > 0):
        #registered face detected
        for person in list_persons_json:
            if (person['personId'] == identify_response_json[0]['candidates'][0]['personId']):
                print "Person Detected: "+person['name']
                set_face_stats(FACE_STATE_RECOGNIZED,person['name'],detect_response_json[0]['faceAttributes']['age'],detect_response_json[0]['faceAttributes']['gender']);
                facialRecognitionPending.clear()
    else:
        # face detected, but not registered
        print "Detected unregistered face as a "+str(detect_response_json[0]['faceAttributes']['age'])+" yr old "+detect_response_json[0]['faceAttributes']['gender']
        set_face_stats(FACE_STATE_NOT_REGISTERED,'',detect_response_json[0]['faceAttributes']['age'],detect_response_json[0]['faceAttributes']['gender']);
        facialRecognitionPending.clear()

def set_face_stats(state,username,age,gender):
    global face_state
    global face_username
    global face_age
    global face_gender
    face_state      = state
    face_username   = username
    face_age        = age
    face_gender     = gender

