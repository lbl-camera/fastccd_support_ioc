#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import socket
import array
from fastccd_support_ioc.utils.cin_functions import WriteReg, ReadReg

# ============================================================================
#					Socket
# ============================================================================
try:
    cin_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.setdefaulttimeout(0.1)

except socket.error as msg:
    cin_sock = None
    print('could not open socket')
    sys.exit(1)


# ============================================================================
#					Functions
# ============================================================================
# ------------------------------------------------------< common functions >

# The readback values are not completely correct until the 3rd pass
# of the configuration serial bit stream is complete
# The sendBiadConfig script calls loadBiasConfigFile twice and 
# readBiasConfigFile once
def readBiasConfigFile(filename):
    #	print " "
    #	print "Loading Configuration File to CCD Camera ...........  "
    #	print "File: " + filename
    engVal = array.array('f', [])
    ii = 0
    with open(filename, 'r') as f:
        file_line = f.readline()
        while file_line != "":
            if (file_line[:1] != "#"):
                read_addr = file_line[:4]
                read_data = file_line[5:9]
                # print read_addr + read_data
                print(f'Writing: {read_data} -> {read_addr}')
                WriteReg(read_addr, read_data, 0)
                time.sleep(0.01)
                if (read_addr == "8001"):
                    bias_raddr = "%0.4X" % (48 + (2 * ii))
                    #					print (bias_raddr)
                    WriteReg("8200", bias_raddr, 0)
                    time.sleep(0.1)
                    retVal = ReadReg("8203")
                    #					print (ii)
                    engVal = float(int((retVal[5:8]), 16))
                    print(("DAC" + str(ii) + " : " + retVal[5:8]))
                    #					print (retVal[4] + " : " + retVal[5:8])
                    #					print ("DAC"+str(ii) + " : " + engVal)
                    ii += 1
            file_line = f.readline()


def loadBiasConfigFile(filename):
    #	print " "
    #	print "Loading Configuration File to CCD Camera ...........  "
    #	print "File: " + filename
    with open(filename, 'r') as f:
        file_line = f.readline()
        while file_line != "":
            if (file_line[:1] != "#"):
                read_addr = file_line[:4]
                read_data = file_line[5:9]
                # print read_addr + read_data
                WriteReg(read_addr, read_data, 0)
            #				time.sleep(0.01)
            file_line = f.readline()
