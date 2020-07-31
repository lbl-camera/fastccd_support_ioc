#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import string
import time
import socket

# ============================================================================
#               System Constants
# ============================================================================
LS325_IP   = "192.168.1.46"
LS325_PORT = 9001

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(3)
s.connect((LS325_IP,LS325_PORT))

# Clear Communications
s.sendall('*CLS\r\n')
# Wait at least 50ms before sending next command
time.sleep(0.1)
# Set Controller to Remote Mode
s.sendall('MODE 1\r\n')
# Wait at least 50ms before sending next command
time.sleep(0.1)
# First Read is a throw-away, so just readback the mode
s.sendall('MODE?\r\n')
# Wait at least 50ms before sending next command
time.sleep(0.1)
m = s.recv(16)
#print m

# Set Loop 1 Heater On
range = str(sys.argv[1])
cmd = ('RANGE 1,'+range+'\r\n')
s.sendall(cmd)
time.sleep(1)

# Query Loop 1 Heater Range
s.sendall('RANGE? 1\r\n')
time.sleep(0.1)
# Wait at least 50ms before sending next command
hr = int(s.recv(16))
#print hr
if hr == 0:
	print "Heater Range  : OFF"
elif hr == 1:
	print "Heater Range  : LOW POWER (2.5W max)"
elif hr == 2:
	print "Heater Range  : HIGH POWER (25W max)"
else:
	print "Return Value out of Range"

s.close()

