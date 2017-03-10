from optparse import OptionParser
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

    # tap generally moves in the Z direction
    # so we'll only use that
    tapAxes = tapAccel.getAxes(True)
    tapInitPos = tapAxes['z']

    tapOpened = False
    calibrated = False
    tapOpenedTime = 0
    tapClosedTime = 0
    calibrationSizeOz = 16
    secPerOz = 0

    while True:

        tapAxes = tapAccel.getAxes(True)
        tapCurrPos = tapAxes['z']

        if (tapOpened):
            ########################## OPENED ##################################
            #check if tap closed
            if (abs(tapCurrPos - tapInitPos) < .2):
                ozPoured = 0
                tapClosedTime = time.time()
                pourTime = tapClosedTime - tapOpenedTime
                if (calibrated == False):
                    print "Calibration Finished:"
                    print str(round(Decimal(pourTime),2))+" seconds for "+str(calibrationSizeOz)+"oz"
                    secPerOz = pourTime/calibrationSizeOz
                    print str(round(Decimal(secPerOz),2))+" seconds per oz\n"
                    send_oz_post(16)
                    # TODO add sanity check here
                    calibrated = True;
                else:
                    ozPoured =  pourTime / secPerOz
                    print "Beer poured: "+str(round(Decimal(ozPoured),2))+"oz in "+str(round(Decimal(pourTime),2))+" seconds on "+time.asctime( time.localtime(tapOpenedTime) );
                    send_oz_post(int(round(ozPoured)))

                tapOpened = False
        else:
            ######################## CLOSED ####################################
            if (abs(tapCurrPos - tapInitPos) > .2):
                if (calibrated == False):
                    print "Calibrating for "+str(calibrationSizeOz)+"oz ..."
                tapOpenedTime = time.time()
                #Start timer TODO
                tapOpened = True


        sleep_time = .25;
        time.sleep(sleep_time);

### END MAIN ####################################################

def send_oz_post(val):
    r = requests.post("http://127.0.0.1:5000/brewing/update_tap.html", data={'oz_poured': val})

if __name__ == "__main__":  
    try:  
        Main()  
    except KeyboardInterrupt:  
        #cleanup()  
        print "Exited\n"
