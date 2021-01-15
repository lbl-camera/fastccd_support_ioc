#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import string
import time
import socket

# ============================================================================
#               System Constants
# ============================================================================
LS325_IP = "192.168.1.46"
LS325_PORT = 9001

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(3)
s.connect((LS325_IP, LS325_PORT))

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
# print m

# ADD arg for value input
# Send New Tempeature Set Point
setPoint = str(sys.argv[1])
cmd = ('SETP 1,' + setPoint + '\r\n')
s.sendall(cmd)
time.sleep(1)

# Query Loop 1 Temperature Set Point
s.sendall('SETP? 1\r\n')
time.sleep(0.1)
# Wait at least 50ms before sending next command
sp = s.recv(16)
print("Temp SetPoint : " + sp[0] + sp[1] + sp[2] + sp[3] + sp[4] + sp[5] + "C")
# print sp

s.close()
