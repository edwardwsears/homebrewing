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

def set_temp_controller_sequence(set_temp,set_range,controlType):
  #send set_temp
  send_and_receive("setTemp\n")
  send_and_receive(set_temp+"\n")
  #send set_range
  send_and_receive("setRange\n")
  send_and_receive(set_range+"\n")
  #send setControlType
  send_and_receive("setControlType\n")
  send_and_receive(controlType+"\n")
  #send end
  send_and_receive("end\n")
  ser.flushInput()
