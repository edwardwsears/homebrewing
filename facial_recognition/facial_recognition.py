import face_api
from picamera import PiCamera
from time import sleep
import requests
import threading


FACE_STATE_PENDING          = 0
FACE_STATE_RECOGNIZED       = 1
FACE_STATE_NOT_REGISTERED   = 2
FACE_STATE_NO_FACE          = 3

# Facial recognition thread
class facial_recognition_thread(threading.Thread):
    def __init__(self,camera):
        threading.Thread.__init__(self)
        self.camera = camera
    def run(self):
        facial_recognition(self.camera)

# Creates facial recognition thread and runs it
def start_facial_recognition_thread(camera):
    if (threading.activeCount() == 1):
        thread = facial_recognition_thread(camera)
        thread.start()
    else:
        print "Thread still running, ignoring request"

# Facial Recognition main function
#
# Takes picture and uses face_api.py to recognize face.
# Updates searsbeers.com db for last pour stats
#
def facial_recognition(camera):

    #camera.annotate_text = "Hey there big boi"
    img_file = "/home/pi/homebrewing/facial_recognition/face_imgs/identify_img.jpg"
    camera.start_preview()
    sleep(2)
    camera.capture(img_file)
    camera.stop_preview()

    send_recognition_post(FACE_STATE_PENDING,"",0,"");
    detect_response_json = face_api.detect_face(img_file)

    if (len(detect_response_json) == 0):
        # no faces detected
        print "No Faces Detected"
        send_recognition_post(FACE_STATE_NO_FACE,"",0,"");
        return

    identify_response_json = face_api.identify_face(detect_response_json[0]['faceId'])
    list_persons_json = face_api.list_persons()

    if (len(identify_response_json[0]['candidates']) > 0):
        #registered face detected
        for person in list_persons_json:
            if (person['personId'] == identify_response_json[0]['candidates'][0]['personId']):
                print "Person Detected: "+person['name']
                send_recognition_post(FACE_STATE_RECOGNIZED,person['name'],detect_response_json[0]['faceAttributes']['age'],detect_response_json[0]['faceAttributes']['gender']);
    else:
        # face detected, but not registered
        print "Detected unregistered face as a "+str(detect_response_json[0]['faceAttributes']['age'])+" yr old "+detect_response_json[0]['faceAttributes']['gender']
        send_recognition_post(FACE_STATE_NOT_REGISTERED,'',detect_response_json[0]['faceAttributes']['age'],detect_response_json[0]['faceAttributes']['gender']);

def send_recognition_post(recognition_state,poured_username,poured_age,poured_gender):
    r = requests.post("http://www.searsbeers.com/set_facial_recognition.html", data={'recognition_state': recognition_state,'poured_username': poured_username,'poured_age': poured_age,'poured_gender': poured_gender})
    return r;
