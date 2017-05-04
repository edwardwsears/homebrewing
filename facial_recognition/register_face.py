from optparse import OptionParser
from picamera import PiCamera
from time import sleep
import face_api

#parse cmdline flags
parser = OptionParser()
parser.add_option("-u","--use",action="store",type="string",dest="user",help="User Name")
(options,args) = parser.parse_args()

if not options.user:
    parser.error('Username (-u) not given')

camera = PiCamera()
camera.rotation=180
camera.resolution = (2592,1944)
camera.framerate = 15
num_pictures = 10

print "*********************************"
print "Begin face registration"
print "*********************************"
sleep(2)
print "Taking "+str(num_pictures)+" pictures"
sleep(1)
print "starting in:"
sleep(1)
print "3"
sleep(1)
print "2"
sleep(1)
print "1"

camera.start_preview()
sleep(2)

for i in range(num_pictures):
    camera.annotate_text = "Picture "+str(i)
    sleep(1)
    camera.annotate_text = ""
    img_file = "/home/pi/homebrewing/facial_recognition/face_imgs/"+options.user+"_training_img_"+str(i)+".jpg"
    camera.capture(img_file)

camera.stop_preview()

#### Create a person #############
print "Creating user: "+options.user
create_person_json = face_api.create_person(options.user)

# Send images to API
for i in range(num_pictures):
    img_file = "/home/pi/homebrewing/facial_recognition/face_imgs/"+options.user+"_training_img_"+str(i)+".jpg"
    print "Sending img: "+img_file
    ##### DETECT ###################
    detect_response_json = face_api.detect_face(img_file)

    ##### ADD FACE ###################
    addface_response_json = face_api.add_face(img_file,create_person_json['personId'],detect_response_json)

print "Scheduling Training"
### Schedule training #######
face_api.train_person_group()


print "Detected as a "+str(detect_response_json[0]['faceAttributes']['age'])+" yr old "+detect_response_json[0]['faceAttributes']['gender']
print "*********************************"
print "Face registration complete"
print "*********************************"
