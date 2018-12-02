EXTRA_CFLAGS=-I$(PWD)/inc

obj-m := temp_control.o
temp_control-objs := src/temp_control_mod.o src/temp_control_sysfs.o src/temp_control_thread.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
