import sys
import os
import glob
import time
import RPi.GPIO as io
io.setmode(io.BCM)

## rpi pins
heat_pin = 23
cool_pin = 24

## Temp probe serial nums #########################
#top on breadboard
BEER_TEMP_PROBE = '28-00000655b9d0'
#bottom on breadboard
CHAMBER_TEMP_PROBE = '28-00000657afb9'

COMPRESSOR_PROTECTION_TIME = 60*30; #30 mins
CONTROL_LOOP_TIME = 2; # check every 2 seconds for control loop
TARGET_LOOP_TIME = 60 * 5; # calculate new target every 5 mins

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
kI_cool =  .2;
kD_cool =  1;

kP_heat =  .7;
kI_heat =  .2;
kD_heat =  1.2;

LOWEST_FRIDGE_TEMP=35;
HIGHEST_FRIDGE_TEMP=100;

# define integral error as global since it persists over time
integral_error = 0
previous_position_error = 0

def calculate_target_temp(set_temp, beer_temp):

  if (set_temp < beer_temp):
      # use *_cool k values
      kP = kP_cool
      kI = kI_cool
      kD = kD_cool
  else:
      # use *_heat k values
      kP = kP_heat
      kI = kI_heat
      kD = kD_heat

  # Algorithm is optimizing for AVG temp, once per cycle
  # P
  position_error = set_temp - beer_temp
  # I
  global integral_error
  integral_error = integral_error + position_error
  # D
  global previous_position_error
  derivitave_error = position_error - previous_position_error
  previous_position_error = position_error

  total_error = position_error*kP + integral_error*kI + derivitave_error*kD
  target = set_temp + total_error

  if (target < LOWEST_FRIDGE_TEMP):
    target = LOWEST_FRIDGE_TEMP
  elif (target > HIGHEST_FRIDGE_TEMP):
    target = HIGHEST_FRIDGE_TEMP


  print("**********************************************\n")
  print("Target Calculation: Position error:   "+str(position_error*kP)+"\n")
  print("                    Integral error:   "+str(integral_error*kI)+"\n")
  print("                    Derivative error: "+str(derivitave_error*kD)+"\n")
  print("                    Target:           "+str(target)+"\n")
  print("**********************************************\n")

  return target


# Initialize avg temp array
AVG_TEMP_ARR_MAX_SIZE = 60 * 60 / CONTROL_LOOP_TIME # keep last 60 mof data
avg_temp_array_size = 0
avg_temp_array_next_idx = 0
avg_temp_array = [0] * AVG_TEMP_ARR_MAX_SIZE

def update_and_get_avg_temp(new_temp):
    global avg_temp_array_size
    global avg_temp_array_next_idx
    global avg_temp_array

    # add new avg to circular array
    avg_temp_array[avg_temp_array_next_idx] = new_temp
    avg_temp_array_next_idx = (avg_temp_array_next_idx + 1) % AVG_TEMP_ARR_MAX_SIZE
    avg_temp_array_size = (avg_temp_array_size + 1) if (avg_temp_array_size < AVG_TEMP_ARR_MAX_SIZE) else avg_temp_array_size

    # calculate and return new avg_temp
    temp_sum = 0
    for temp in avg_temp_array:
        temp_sum = temp_sum + temp

    return temp_sum/avg_temp_array_size
