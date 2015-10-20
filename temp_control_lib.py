import sys
import time

#if you only want to send data to arduino (i.e. a signal to move a servo)
## generally should not be used
def send(ser, theinput ):
  ser.write( theinput )
  while True:
    try:
      time.sleep(0.01)
      break
    except:
      pass
  time.sleep(0.1)

#if you would like to tell the arduino that you would like to receive data from the arduino
##should always use this one
def send_and_receive(ser, theinput ):
  ser.write( theinput )
  while True:
    try:
      time.sleep(0.01)
      state = ser.readline()
      return state
    except:
      pass
  time.sleep(0.1)

def set_temp_controller_sequence(ser,set_temp,set_range,controlType):
  #send set_temp
  send_and_receive(ser,"setTemp\n")
  send_and_receive(ser,set_temp+"\n")
  #send set_range
  send_and_receive(ser,"setRange\n")
  send_and_receive(ser,set_range+"\n")
  #send setControlType
  send_and_receive(ser,"setControlType\n")
  send_and_receive(ser,controlType+"\n")
  #send end
  send_and_receive(ser,"end\n")
  ser.flushInput()

#returns current temperature on temp probe
#must have initialized serial and temp controller
def poll_temp_probe(ser):
  temp_received = False
  while (temp_received==False):
    try:
      send_and_receive(ser,"sendTemp\n")
      curr_temp = float(send_and_receive(ser,"ready\n"))
      ser.flushInput()
      temp_received = True;
    except serial.serialutil.SerialException:
      ## reset serail connection if failed
      ser.close()
      ser = serial.Serial('/dev/ttyACM0', 9600)
      ser.flushInput()
      temp_received = False;
      time.sleep(2);
  return curr_temp
