# USAGE
# 1. Configure circular logfile:
# %>  sudo logrotate logrotate_ferm_chamber_temp.cfg
# 2. Start chamber controller with nohup
# %> nohup python ferm_chamber_controller_v2.py >> /tmp/ferm_chamber_temp.log &

from optparse import OptionParser
import sys
import time
##sending email
from subprocess import call
import os
##regex
import re
##temp control file
import temp_control_lib
import requests
import datetime
from decimal import *

#MAIN
def Main():

    ## Initializations ##################
    global lastChamberSetData
    lastChamberSetData = {'set_temp' : 65, 'set_range' : 2, 'temp_control_on' : 0}
    curr_temp = 65
    #setup io pins
    temp_control_lib.io_setup()

    chamberSetData = get_chamber_set_data();

    print("Temp Control On: "+str(chamberSetData['temp_control_on'])+"\n")
    print("Temperature set point: "+str(chamberSetData['set_temp'])+"F with range of "+str(chamberSetData['set_range'])+"F\n")

    ##initialize control vars
    curr_beer_temp = temp_control_lib.read_temp(temp_control_lib.BEER_TEMP_PROBE)
    last_update = datetime.datetime.now()

    # start avg_avg with current temp
    avg_temp = temp_control_lib.update_and_get_avg_temp(curr_beer_temp)
    target_temp = temp_control_lib.calculate_target_temp(chamberSetData['set_temp'], curr_beer_temp);
    send_temp_post(curr_beer_temp,avg_temp)

    last_target_calculation_time = 0

    ## STATE VARS ###################
    ## chamber_state options:
    ## OFF
    ## HEATING
    ## COOLING
    CHAMBER_STATE = "OFF"
    CHAMBER_STATE_NEXT = "OFF"
    LAST_COMPRESSOR_ON = 0;
    LAST_HEAT_ON = 0;
    temp_control_lib.set_heat_ssr(False);
    temp_control_lib.set_cool_ssr(False);

    while True:
        string_time = time.asctime( time.localtime(time.time()) );
        print(string_time+"\n")

        chamberSetData = get_chamber_set_data();
        if (chamberSetData['temp_control_on'] != 1):
            print("Temp Control Off\n")
            temp_control_lib.set_cool_ssr(False);
            temp_control_lib.set_heat_ssr(False);
            CHAMBER_STATE = "OFF"
            CHAMBER_STATE_NEXT = "OFF"
            time.sleep(60*5); #sleep for 5 mins
            continue;

        ##poll temperature probe
        curr_beer_temp = temp_control_lib.read_temp(temp_control_lib.BEER_TEMP_PROBE)
        curr_chamber_temp = temp_control_lib.read_temp(temp_control_lib.CHAMBER_TEMP_PROBE)

        print("current set temp " + str(chamberSetData['set_temp']) + "\n")
        print("current beer temp " + str(curr_beer_temp) + "\n")
        print("current chamber temp " + str(curr_chamber_temp) + "\n")
        print("target_temp: " + str(target_temp) + "\n")
        print("avg temp: " + str(avg_temp) + "\n")
        print("Chamber State: " + str(CHAMBER_STATE) + "\n\n")

        #update db
        if ((datetime.datetime.now() - last_update).seconds > (15*60)):
            last_update = datetime.datetime.now()
            send_temp_post(curr_beer_temp,avg_temp)

        #update averages
        avg_temp = temp_control_lib.update_and_get_avg_temp(curr_beer_temp)

        CURR_TIME = time.time();

        # only calculate target every so often
        if ( CURR_TIME > (last_target_calculation_time + temp_control_lib.TARGET_LOOP_TIME) ):
            target_temp = temp_control_lib.calculate_target_temp(chamberSetData['set_temp'], curr_beer_temp);
            last_target_calculation_time = CURR_TIME

        ##control SSRs and control logic (PI)
        if (CHAMBER_STATE == "COOLING"):
          compressor_on_time = CURR_TIME - LAST_COMPRESSOR_ON;
          if (curr_chamber_temp < target_temp):

            ##############
            # COOL -> OFF
            ##############

            CHAMBER_STATE_NEXT = "OFF"
            temp_control_lib.set_cool_ssr(False);

        elif (CHAMBER_STATE == "HEATING"):
          heater_on_time = CURR_TIME - LAST_HEAT_ON;
          if (curr_chamber_temp > target_temp):

            ##############
            # HEAT -> OFF
            ##############

            CHAMBER_STATE_NEXT = "OFF"
            temp_control_lib.set_heat_ssr(False);

        elif (CHAMBER_STATE == "OFF"):

          if (curr_beer_temp > (chamberSetData['set_temp'] + chamberSetData['set_range'])):

            ##############
            # OFF -> COOL
            ##############

            fridge_off_time = CURR_TIME - LAST_COMPRESSOR_ON
            if (fridge_off_time < temp_control_lib.COMPRESSOR_PROTECTION_TIME):
              print("WAITING - Fridge off time: " + str(fridge_off_time) + "\n")
            else:
              LAST_COMPRESSOR_ON = CURR_TIME;
              temp_control_lib.set_cool_ssr(True);

              CHAMBER_STATE_NEXT = "COOLING"

          elif (curr_beer_temp < (chamberSetData['set_temp'] - chamberSetData['set_range'])):

            ##############
            # OFF -> HEAT
            ##############

            CHAMBER_STATE_NEXT = "HEATING"
            temp_control_lib.set_heat_ssr(True);
            LAST_HEAT_ON = CURR_TIME;

        CHAMBER_STATE = CHAMBER_STATE_NEXT;
        time.sleep(temp_control_lib.CONTROL_LOOP_TIME);

### END MAIN ####################################################

def send_temp_post(temp,average):
    try:
        temp = round(Decimal(temp),2)
        r = requests.post("http://www.searsbeers.com/update_temp.html", data={'temp' : temp,'average':average})
    except:
        print("Temp Post Failed\n")

def get_chamber_set_data():
    global lastChamberSetData
    try:
        r = requests.get("http://www.searsbeers.com/get_chamber_set_data.html", )
        r = r.json()
        lastChamberSetData = r
    except:
        # if fails use last received data
        print("get_chamber_set_data() Failed\n")
        r = lastChamberSetData

    return r

if __name__ == "__main__":
  try:
    Main()
  except KeyboardInterrupt:
    temp_control_lib.io.cleanup()

