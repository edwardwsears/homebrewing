import sys
import os
import glob
import time
import RPi.GPIO as io
io.setmode(io.BCM)

## rpi pins
heat_pin = 23
cool_pin = 24

 
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
 
def read_temp_raw(serial_num):
    device_file = base_dir + '/' + serial_num + '/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
#fn to read temp from temp sensor
## returns temp in deg F
def read_temp(serial_num):
    lines = read_temp_raw(serial_num)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(serial_num)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f

# fns to control SSRs
def io_setup():
  io.setup(heat_pin,io.OUT)
  io.setup(cool_pin,io.OUT)
def set_cool_ssr(value):
  io.output(cool_pin,value)
def set_heat_ssr(value):
  io.output(heat_pin,value)

kP_cool =  1;
kP_heat =  1;
kI_cool =  1;
kI_heat =  1;
kD_cool =  1;
kD_heat =  1;
LOWEST_FRIDGE_TEMP=35;


def calculate_target_temp(set_temp,beer_temp,avg_temp,avg_avg_temp):
  position_error = (beer_temp - set_temp) * kP_cool
  integral_error = (avg_temp - set_temp) * kI_cool
  derivative_error = (avg_avg_temp - set_temp) * kD_cool
  control_undershoot = position_error + integral_error + derivative_error;
  target = set_temp - control_undershoot
  if (target < LOWEST_FRIDGE_TEMP):
    target = LOWEST_FRIDGE_TEMP
  return target

