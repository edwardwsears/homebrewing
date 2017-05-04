from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation=180
camera.start_preview()
camera.annotate_text = "Contrast 50"
sleep(5)
camera.stop_preview()
