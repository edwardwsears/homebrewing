import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_pdf import PdfPages
from optparse import OptionParser
import sys
import time
##sending email
from subprocess import call
import os
##comunicating with ardiono
import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2); ## sleep 2 secs to allow board to reset
##regex
import re
##temp control file
import temp_control_lib


#MAIN

#parse cmdline flags
parser = OptionParser()
parser.add_option("-n","--brew_name",action="store",type="string",dest="brew_name",help="Brew Name")
parser.add_option("-s","--set_temp",action="store",type="int",dest="set_temp",help="Temperature Set Point")
parser.add_option("-r","--set_range",action="store",type="int",dest="set_range",help="Temperature Range (in F from set point)")
parser.add_option("-c","--cool",action="store_true",dest="cool",help="Cooling temp control")
parser.add_option("-t","--heat",action="store_true",dest="heat",help="heating temp control")
parser.add_option("-d","--dual_stage",action="store_true",dest="dual_stage",help="heating temp control")
parser.add_option("-e","--email",action="store",type="string",dest="email",default="edwardwsears@gmail.com",help="Email to send to")
##parser.add_option("-g","--graphs_only",action="store_true",dest="graphs_only",default=False,help="Only generate graphs (no stats)")
(options,args) = parser.parse_args()

#initialize
curr_temp = 65;
out_of_range = 0;
ser.flushInput()

print options.brew_name + " temperature tracking\n"
print "Temperature set point: "+str(options.set_temp)+"F with range of "+str(options.set_range)+"F\n"

controlType = ""
if (options.cool):
  controlType = "canCool"
elif (options.heat):
  controlType = "canHeat"
elif (options.dual_stage):
  controlType = "dualControl"

set_temp_controller_sequence(str(options.set_temp),str(options.set_range),controlType)

while True:
    ##poll temperature probe
    ##ser.flushInput()
    temp_received = False
    while (temp_received==False):
      try:
        send_and_receive("sendTemp\n")
        curr_temp = float(send_and_receive("ready\n"))
        ser.flushInput()
        temp_received = True;
      except serial.serialutil.SerialException:
        ## reset serail connection if failed
        ser.close()
        ser = serial.Serial('/dev/ttyACM0', 9600)
        ser.flushInput()
        temp_received = False;
        time.sleep(2);
    string_time = time.asctime( time.localtime(time.time()) );
    print string_time+"\n"
    print "current temp " + str(curr_temp) + "\n"

    ####check for range, send email if out
    ##email_delta_limit = options.set_range + 1; # degrees off of range to send email
    ##if (((curr_temp > (options.upper_limit+email_delta_limit)) or (curr_temp < (options.lower_limit - email_delta_limit))) and out_of_range == 0):
    ##    out_of_range = 1;
    ##    temp_out_of_range = curr_temp;
    ##    print "Temperature out of range. Sending email\n"
    ##    body = options.brew_name+" is at "+str(curr_temp)+"F\n"
    ##    body += "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"
    ##    cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" out of range\" edwardwsears@gmail.com"
    ##    os.system(cmd)

    ##elif ((curr_temp < options.upper_limit) and (curr_temp > options.lower_limit) and out_of_range == 1):
    ##    ## temp comes back in range
    ##    out_of_range = 0;
    ##    print "Temperature back in range. Sending email\n"
    ##    body = options.brew_name+" is at "+str(curr_temp)+"F\n"
    ##    body += "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"
    ##    cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" back in range\" edwardwsears@gmail.com"
    ##    os.system(cmd)
    ##elif (((curr_temp-temp_out_of_range)>1) and (out_of_range == 1)):
    ##    ## temp out of range and changed a degree
    ##    temp_out_of_range = curr_temp;
    ##    print "Temperature out of range changed. Sending email\n"
    ##    body = options.brew_name+" is at "+str(curr_temp)+"F\n"
    ##    body += "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"
    ##    cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" out of range\" edwardwsears@gmail.com"
    ##    os.system(cmd)
      

    ##sleep_time = 30*60; #30 mins in seconds
    sleep_time = 20; #check every 20 seconds
    time.sleep(sleep_time);
