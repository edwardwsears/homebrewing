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


#MAIN
def Main():

  #parse cmdline flags
  parser = OptionParser()
  parser.add_option("-n","--brew_name",action="store",type="string",dest="brew_name",help="Brew Name")
  parser.add_option("-s","--set_temp",action="store",type="int",dest="set_temp",help="Temperature Set Point")
  parser.add_option("-r","--set_range",action="store",type="int",dest="set_range",help="Temperature Range (in F from set point)")
  parser.add_option("-c","--cool",action="store_true",dest="cool",help="Cooling temp control")
  parser.add_option("-t","--heat",action="store_true",dest="heat",help="heating temp control")
  parser.add_option("-d","--dual_stage",action="store_true",dest="dual_stage",help="heating and cooling temp control")
  parser.add_option("-e","--email",action="store",type="string",dest="email",default="edwardwsears@gmail.com",help="Email to send to")
  parser.add_option("-i","--first",action="store_true",dest="first_reading",help="specifies first reading of brew")
  ##parser.add_option("-g","--graphs_only",action="store_true",dest="graphs_only",default=False,help="Only generate graphs (no stats)")
  (options,args) = parser.parse_args()

  #implement dual_stage option
  if (options.dual_stage):
    options.cool = True;
    options.heat = True;

  ## Initializations ##################
  sleep_time = 5; #check every 5 seconds
  curr_temp = 65
  #setup io pins
  temp_control_lib.io_setup()

  print options.brew_name + " fermentation temperature tracking\n"
  print "Temperature set point: "+str(options.set_temp)+"F with range of "+str(options.set_range)+"F\n"
  print "Heating: " + str(options.heat) + ", Cooling: "+str(options.cool)+"\n"

  ## Temp probe serial nums #########################
  #top on breadboard
  BEER_TEMP_PROBE = '28-00000655b9d0'
  #bottom on breadboard
  CHAMBER_TEMP_PROBE = '28-00000657afb9'

  ## compressor protection time (in s)
  COMPRESSOR_PROTECTION_TIME = 60*30; #30 mins

  ##initialize control vars
  curr_beer_temp = temp_control_lib.read_temp(BEER_TEMP_PROBE)
  update_db(curr_beer_temp,options.first_reading)
  last_update = datetime.datetime.now()
  avg_temp = curr_beer_temp
  avg_temp_sum = curr_beer_temp
  avg_temp_num_samples = 1
  avg_avg_temp = curr_beer_temp
  avg_avg_temp_sum = curr_beer_temp
  avg_avg_temp_num_samples = 1
  AVG_AVG_SAMPLES_RESET = 60
  TARGET_TEMP = temp_control_lib.calculate_target_temp(options.set_temp,curr_beer_temp,avg_temp,avg_avg_temp);

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
    ##poll temperature probe
    curr_beer_temp = temp_control_lib.read_temp(BEER_TEMP_PROBE)
    curr_chamber_temp = temp_control_lib.read_temp(CHAMBER_TEMP_PROBE)
    string_time = time.asctime( time.localtime(time.time()) );
    print string_time+"\n"
    print "current beer temp " + str(curr_beer_temp) + "\n"
    print "current chamber temp " + str(curr_chamber_temp) + "\n"
    print "TARGET_TEMP: " + str(TARGET_TEMP) + "\n"
    print "avg temp: " + str(avg_temp) + "\n"
    print "avg avg temp: " + str(avg_avg_temp) + "\n"
    print "Chamber State: " + str(CHAMBER_STATE) + "\n\n"

    #update db
    if ((datetime.datetime.now() - last_update).minutes > 30):
        update_db(curr_beer_temp,False)

    #update averages
    avg_temp_sum += curr_beer_temp
    avg_temp_num_samples += 1
    avg_temp = avg_temp_sum/avg_temp_num_samples

    ##control SSRs and control logic (PI)
    CURR_TIME = time.time();
    if (CHAMBER_STATE == "COOLING"):
      compressor_on_time = CURR_TIME - LAST_COMPRESSOR_ON;
      if (curr_chamber_temp < TARGET_TEMP):
        CHAMBER_STATE_NEXT = "OFF"
        temp_control_lib.set_cool_ssr(False);
        sleep_time = 5
    elif (CHAMBER_STATE == "HEATING"):
      heater_on_time = CURR_TIME - LAST_HEAT_ON;
      if (curr_chamber_temp > TARGET_TEMP):
        CHAMBER_STATE_NEXT = "OFF"
        temp_control_lib.set_heat_ssr(False);
        sleep_time = 5
    elif (CHAMBER_STATE == "OFF"):
      TARGET_TEMP = temp_control_lib.calculate_target_temp(options.set_temp,curr_beer_temp,avg_temp,avg_avg_temp);
      if ((curr_beer_temp > (options.set_temp + options.set_range)) and options.cool and (TARGET_TEMP<curr_chamber_temp)):
        #too hot, cool down to set point
        CHAMBER_STATE_NEXT = "COOLING"

        ##reset avgs
        avg_temp_sum = 0
        avg_temp_num_samples = 0
        #avg of the avg_temp = Derivitive term
        avg_avg_temp_sum += avg_temp
        avg_avg_temp_num_samples += 1
        #keep avg avg to a reasonable size. At AVG_AVG_SAMPLES_RESET samples, reset to AVG_AVG_SAMPLES_RESET/2
        if (avg_avg_temp_num_samples >= AVG_AVG_SAMPLES_RESET):
          avg_avg_temp_num_samples = avg_avg_temp_num_samples/2
          avg_avg_temp_sum = avg_avg_temp_sum/2
        avg_avg_temp = avg_avg_temp_sum/avg_avg_temp_num_samples


      elif ((curr_beer_temp < (options.set_temp - options.set_range)) and options.heat and (TARGET_TEMP>curr_chamber_temp)):
        #too hot, cool down to set point
        temp_control_lib.set_heat_ssr(True);
        CHAMBER_STATE_NEXT = "HEATING"
        LAST_HEAT_ON = CURR_TIME;
        sleep_time = 1

        ##calculate target temp
        #reset avgs
        avg_temp_sum = 0
        avg_temp_num_samples = 0
        #avg of the avg_temp = Derivitive term
        avg_avg_temp_sum += avg_temp
        avg_avg_temp_num_samples += 1 
        #keep avg avg to a reasonable size. At AVG_AVG_SAMPLES_RESET samples, reset to AVG_AVG_SAMPLES_RESET/2
        if (avg_avg_temp_num_samples >= AVG_AVG_SAMPLES_RESET):
          avg_avg_temp_num_samples = avg_avg_temp_num_samples/2
          avg_avg_temp_sum = avg_avg_temp_sum/2
        avg_avg_temp = avg_avg_temp_sum/avg_avg_temp_num_samples

    #set state w/ 30m compressor switch protection
    if ((CHAMBER_STATE == "OFF") and (CHAMBER_STATE_NEXT == "COOLING")):
        
      fridge_off_time = CURR_TIME - LAST_COMPRESSOR_ON 
      if ((CURR_TIME - LAST_COMPRESSOR_ON) > COMPRESSOR_PROTECTION_TIME):
        CHAMBER_STATE = CHAMBER_STATE_NEXT;
        LAST_COMPRESSOR_ON = CURR_TIME;
        temp_control_lib.set_cool_ssr(True);
      else:
        print "WAITING - Fridge off time: " + str(fridge_off_time) + "\n"
    else:
      CHAMBER_STATE = CHAMBER_STATE_NEXT;

    time.sleep(sleep_time);
          
### END MAIN ####################################################

if __name__ == "__main__":  
  try:  
    Main()  
  except KeyboardInterrupt:  
    temp_control_lib.io.cleanup()  

def update_db(temp,firs_reading):
    if (first_reading):
        send_temp_post(temp,True)
    else:
        send_temp_post(temp,False)

def send_temp_post(temp,first):
    r = requests.post("http://ec2-52-40-75-70.us-west-2.compute.amazonaws.com/update_temp.html", data={'temp' : temp,'first':first})
