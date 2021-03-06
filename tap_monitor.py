from optparse import OptionParser
from facial_recognition import facial_recognition
from picamera import PiCamera
import threading
import sys
import time
##regex
import re
import adxl345
from decimal import *
import requests

#initial setup
tapAccel = adxl345.ADXL345()

#MAIN
def Main():

    #parse cmdline flags
    parser = OptionParser()
    parser.add_option("-c","--calibrate",action="store_true",dest="do_calibrate",help="Calibrate tap flow at start")
    (options,args) = parser.parse_args()

    # tap generally moves in the Z direction
    # so we'll only use that
    tapAxes = tapAccel.getAxes(True)
    tapInitPos = tapAxes['z']

    tapOpened = False
    calibrated = False
    accelReadSuccess = False
    tapOpenedTime = 0
    tapClosedTime = 0
    calibrationSizeOz = 16

    accel_z_thresh = .3

    # pi camera init
    camera = PiCamera()
    camera.rotation=180
    camera.resolution = (2592,1944)
    camera.framerate = 15

    #threading condition variables
    facialRecognitionPending = threading.Event()

    if (options.do_calibrate == True):
        secPerOz = 0
        print "Calibrating on next pour"
    else:
        secPerOz = get_sec_per_oz_data()
        print "Calibrated to "+str(secPerOz)+" sec/oz"

    while True:

        accelReadSuccess = False
        while (accelReadSuccess == False):
            try:
                tapAxes = tapAccel.getAxes(True)
                accelReadSuccess = True
            except IOError:
                time.sleep(1);

        tapCurrPos = tapAxes['z']

        if (tapOpened):
            ########################## IS OPENED ##################################
            #check if tap closed
            if (abs(tapCurrPos - tapInitPos) < accel_z_thresh):
                ozPoured = 0
                tapClosedTime = time.time()
                pourTime = tapClosedTime - tapOpenedTime
                if ((calibrated == False) and (options.do_calibrate == True)):
                    print "Calibration Finished:"
                    print str(round(Decimal(pourTime),2))+" seconds for "+str(calibrationSizeOz)+"oz"
                    secPerOz = pourTime/calibrationSizeOz
                    print str(round(Decimal(secPerOz),2))+" seconds per oz\n"
                    send_oz_post_threaded(16,facialRecognitionPending)
                    send_sec_per_oz_post(round(Decimal(secPerOz),2))
                    # TODO add sanity check here
                    calibrated = True;
                else:
                    ozPoured =  pourTime / secPerOz
                    print "Beer poured: "+str(round(Decimal(ozPoured),2))+"oz in "+str(round(Decimal(pourTime),2))+" seconds on "+time.asctime( time.localtime(tapOpenedTime) );
                    if (ozPoured>1):
                        send_oz_post_threaded(int(round(ozPoured)),facialRecognitionPending)

                tapOpened = False
        else:
            ######################## IS CLOSED ####################################
            if (abs(tapCurrPos - tapInitPos) > accel_z_thresh):
                if ((calibrated == False) and (options.do_calibrate == True)):
                    print "Calibrating for "+str(calibrationSizeOz)+"oz ..."
                # Start facial recognition thread
                facial_recognition.start_facial_recognition_thread(camera, facialRecognitionPending)
                tapOpenedTime = time.time()
                tapOpened = True


        sleep_time = .25;
        time.sleep(sleep_time);

### END MAIN ####################################################

class oz_post_thread(threading.Thread):
    def __init__(self,val,facialRecognitionPending):
        threading.Thread.__init__(self)
        self.val = val
        self.facialRecognitionPending = facialRecognitionPending
    def run(self):
        send_oz_post(self.val,self.facialRecognitionPending)

def send_oz_post_threaded(val,facialRecognitionPending):
    thread = oz_post_thread(val,facialRecognitionPending)
    thread.start()

def send_oz_post(val,facialRecognitionPending):
    if (facialRecognitionPending.is_set()):
        #facial recognition is pending, wait for it to return
        facialRecognitionPending.wait()

    #facial recognition is finished, send post
    r = requests.post("http://www.searsbeers.com/update_tap.html", data={'oz_poured': val,'recognition_state': facial_recognition.face_state,'poured_username': facial_recognition.face_username,'poured_age': facial_recognition.face_age,'poured_gender': facial_recognition.face_gender})
    return r;

def send_sec_per_oz_post(val):
    r = requests.post("http://www.searsbeers.com/update_sec_per_oz_data.html", data={'sec_per_oz': val})

def get_sec_per_oz_data():
    r = requests.get("http://www.searsbeers.com/get_sec_per_oz_data.html", )
    r = r.json()
    return r['sec_per_oz']

if __name__ == "__main__":  
    try:  
        Main()  
    except KeyboardInterrupt:  
        #cleanup()  
        print "Exited\n"
