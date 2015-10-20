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
parser.add_option("-e","--email",action="store",type="string",dest="email",default="edwardwsears@gmail.com",help="Email to send to")
##parser.add_option("-g","--graphs_only",action="store_true",dest="graphs_only",default=False,help="Only generate graphs (no stats)")
(options,args) = parser.parse_args()

#initialize
curr_temp = 100
warning20F = False
warning10F = False
warning0F = False

print options.brew_name + " ekettle temperature tracking\n"
print "Temperature set point: "+str(options.set_temp)+"F\n"

temp_control_lib.set_temp_controller_sequence(ser,str(options.set_temp),str(options.set_range),"canHeat")

while True:
    ##poll temperature probe
    curr_temp = poll_temp_probe()
    string_time = time.asctime( time.localtime(time.time()) );
    print string_time+"\n"
    print "current temp " + str(curr_temp) + "\n"

    ##check for range, send email if out
    if (curr_temp>(options.set_temp-20) && !warning20F):
        #send 20 deg warning
        print "Within 20 Degrees. Sending email\n"
        body = options.brew_name+" is at "+str(curr_temp)+"F\n"
        body += "Temperature Set Point "+str(options.set_temp)+"F \n"
        cmd = "echo \""+body+"\" | mutt -s \"eKettle Monitor: "+options.brew_name+" within 20F\" "+options.email
        os.system(cmd)
    elif (curr_temp>(options.set_temp-10) && !warning10F):
        #send 10 deg warning
        print "Within 10 Degrees. Sending email\n"
        body = options.brew_name+" is at "+str(curr_temp)+"F\n"
        body += "Temperature Set Point "+str(options.set_temp)+"F \n"
        cmd = "echo \""+body+"\" | mutt -s \"eKettle Monitor: "+options.brew_name+" within 10F\" "+options.email
        os.system(cmd)
    elif (curr_temp>(options.set_temp-options.set_range) && !warning0F):
        #send 0 deg warning
        print "Temp at Set Point. Sending email\n"
        body = options.brew_name+" is at "+str(curr_temp)+"F\n"
        body += "Temperature Set Point "+str(options.set_temp)+"F \n"
        cmd = "echo \""+body+"\" | mutt -s \"eKettle Monitor: "+options.brew_name+" is at set point\" "+options.email
        os.system(cmd)

    

    ##sleep_time = 30*60; #30 mins in seconds
    sleep_time = 20; #check every 20 seconds
    time.sleep(sleep_time);
