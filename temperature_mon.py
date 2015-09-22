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


#Helper Functions

#if you only want to send data to arduino (i.e. a signal to move a servo)
def send( theinput ):
  ser.write( theinput )
  while True:
    try:
      time.sleep(0.01)
      break
    except:
      pass
  time.sleep(0.1)

#if you would like to tell the arduino that you would like to receive data from the arduino
def send_and_receive( theinput ):
  ser.write( theinput )
  while True:
    try:
      time.sleep(0.01)
      state = ser.readline()
      return state
    except:
      pass
  time.sleep(0.1)


#MAIN

#parse cmdline flags
parser = OptionParser()
parser.add_option("-n","--brew_name",action="store",type="string",dest="brew_name",help="Brew Name")
parser.add_option("-u","--upper_limit",action="store",type="float",dest="upper_limit",help="Upper Temperature Limit")
parser.add_option("-l","--lower_limit",action="store",type="float",dest="lower_limit",help="Lower Temperature Limit")
parser.add_option("-c","--cool",action="store_true",dest="cool",help="Cooling temp control")
parser.add_option("-t","--heat",action="store_false",dest="cool",help="heating temp control")
parser.add_option("-e","--email",action="store",type="string",dest="email",default="edwardwsears@gmail.com",help="Email to send to")
##parser.add_option("-g","--graphs_only",action="store_true",dest="graphs_only",default=False,help="Only generate graphs (no stats)")
(options,args) = parser.parse_args()

#initialize
curr_temp = 65;
temp_history = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]; ##24 hr history
out_of_range = 0;
temp_out_of_range = 0;
summary_sent=0;
ser.flushInput()

print options.brew_name + " temperature tracking\n"
print "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"

while True:
    ##poll temperature probe
    ##ser.flushInput()
    temp_received = False;
    while (temp_received==False):
      try:
        curr_temp = float(send_and_receive('1'))
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
    curr_hour = time.localtime(time.time())[3]
    temp_history[curr_hour] = curr_temp;

    ##temp control logic
    if (curr_temp > options.upper_limit):
      #above temp
      if (options.cool): 
        #turn on cool
        send('2'); 
      else:
        #turn off heat
        send('3'); 
    elif (curr_temp < options.lower_limit):
      #below temp
      if (options.cool):
        #turn off cool
        send('3'); 
      else:
        #turn on heat
        send('2');

    ##check for range, send email if out
    email_delta_limit = 2; # degrees off of range to send email
    if (((curr_temp > (options.upper_limit+email_delta_limit)) or (curr_temp < (options.lower_limit - email_delta_limit))) and out_of_range == 0):
        out_of_range = 1;
        temp_out_of_range = curr_temp;
        print "Temperature out of range. Sending email\n"
        body = options.brew_name+" is at "+str(curr_temp)+"F\n"
        body += "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"
        cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" out of range\" edwardwsears@gmail.com"
        os.system(cmd)

    elif ((curr_temp < options.upper_limit) and (curr_temp > options.lower_limit) and out_of_range == 1):
        ## temp comes back in range
        out_of_range = 0;
        print "Temperature back in range. Sending email\n"
        body = options.brew_name+" is at "+str(curr_temp)+"F\n"
        body += "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"
        cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" back in range\" edwardwsears@gmail.com"
        os.system(cmd)
    elif (((curr_temp-temp_out_of_range)>1) and (out_of_range == 1)):
        ## temp out of range and changed a degree
        temp_out_of_range = curr_temp;
        print "Temperature out of range changed. Sending email\n"
        body = options.brew_name+" is at "+str(curr_temp)+"F\n"
        body += "Temperature Range: "+str(options.lower_limit)+"F - "+str(options.upper_limit)+"F\n"
        cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" out of range\" edwardwsears@gmail.com"
        os.system(cmd)
      

    ## each day send summary email from previous day
    summary_hour = 4+12;
    if (curr_hour==summary_hour and summary_sent==0):
        print "Sending Summary Email\n"
        body = "Temperature summary for "+options.brew_name+":\n"
        body += string_time+"\n"
        body += "Time: Degrees F\n"
        for i in range(summary_hour+1,24):
          body += str(i)+": "+str(temp_history[i])+" F\n"
        for i in range(0,summary_hour+1):
          body += str(i)+": "+str(temp_history[i])+" F\n"
        cmd = "echo \""+body+"\" | mutt -s \"Brew Monitor: "+options.brew_name+" daily summary\" edwardwsears@gmail.com"
        os.system(cmd)
        summary_sent=1;
    elif (curr_hour!=summary_hour):
        summary_sent=0;
      
    
    ##sleep_time = 30*60; #30 mins in seconds
    sleep_time = 20; #check every 20 seconds
    time.sleep(sleep_time);
