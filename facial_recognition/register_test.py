import httplib, urllib, base64
import json
import face_api


#### Create a person #############
create_person_json = face_api.create_person("esears")

##### DETECT ###################
detect_response_json = face_api.detect_face("/home/pi/homebrewing/facial_recognition/face_imgs/esears_training_img_0.jpg")

##### ADD FACE ###################
addface_response_json = face_api.add_face("/home/pi/homebrewing/facial_recognition/face_imgs/esears_training_img_0.jpg",create_person_json['personId'],detect_response_json)

print "****************"
print "Registered "+str(detect_response_json[0]['faceAttributes']['age'])+" yr old "+detect_response_json[0]['faceAttributes']['gender']
print "****************"

##### Delete person ############################

face_api.delete_person(create_person_json['personId'])
