#!/usr/bin/env python3

import can 
import time
from threading import Timer
import sys

i=0

print("started")
can_channel = 'vcan0'
#channel=name des interface

id = int(sys.argv[1])
data_in = int(sys.argv[2])

bus = can.interface.Bus(can_channel, bustype='socketcan_native')
message=can.Message(extended_id=False)
message.arbitration_id=id
a=6
liste=[0,1,2,3,4,5,a,7]
message.data=bytearray(liste)

print("Kury vor Start")
time.sleep(5)
print("Start")
try:
	while 1:
		bus.send(message)
		print(message.data)
		time.sleep(0.01)
		if a<250:
			a+=1
		else:
			a=0
		message.data=bytearray([0,1,2,3,4,5,a,7])
		i=i+1
	
except KeyboardInterrupt:
	bus.shutdown()
	print("Keine weitere Nachrichten")
