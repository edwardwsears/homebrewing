#!/bin/bash
insmod temp_control.ko
echo "Read Set Temp setting:"
cat /sys/temp_control/set_temp
echo "Setting Set Temp to 65"
echo 65 > /sys/temp_control/set_temp
echo "Read Set Temp setting:"
cat /sys/temp_control/set_temp
echo "Read Current Temp:"
cat /sys/temp_control/current_temp
echo "dmesg log:"
rmmod temp_control
dmesg -c
