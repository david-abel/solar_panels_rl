#testing arduino serial_loc

import serial
import time

ser = serial.Serial('/dev/cu.usbmodem1421', 9600)
print "initializing connection"
time.sleep(2)

while True:
    #write to Arduino
    ser.write("TEST")
    print ser.readline()
    time.sleep(1)
