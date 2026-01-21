# kernel/ll_driver/Makefile
obj-m += ll_driver.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f *.o *.ko *.mod.c modules.order Module.symvers

install:
	sudo insmod ll_driver.ko

remove:
	sudo rmmod ll_driver

test:
	sudo dmesg -C
	sudo insmod ll_driver.ko
	sudo chmod 666 /dev/ll_driver
	dmesg | tail -20
