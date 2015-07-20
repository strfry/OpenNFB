#!/bin/sh

sudo kextunload -b com.FTDI.driver.FTDIUSBSerialDriver
sudo kextload -b com.FTDI.driver.FTDIUSBSerialDriver
sleep 1
ls /dev/tty.OpenBCI-DN009616
