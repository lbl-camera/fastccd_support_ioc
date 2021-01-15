#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
import socket
from fastccd_support_ioc.utils.cin_functions import WriteReg, ReadReg

BIAS_AND_VOLTAGE_RANGES = [9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           99.,
                           5.,
                           -15.,
                           -25.,
                           -10.,
                           -5.1,
                           0.,
                           0.]


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
    last_written_value = None
    ii = 0
    with open(filename, 'r') as f:
        file_line = f.readline()
        while file_line != "":
            if (file_line[:1] != "#"):
                read_addr = file_line[:4]
                read_data = file_line[5:9]
                # print read_addr + read_data
                if read_addr == '8201':
                    print(f'Writing: {read_data} -> {read_addr}')
                WriteReg(read_addr, read_data, 0)
                time.sleep(0.01)
                if (read_addr == "8001"):
                    bias_raddr = "%0.4X" % (48 + (2 * ii))
                    #					print (bias_raddr)
                    WriteReg("8200", bias_raddr, 0)
                    time.sleep(0.2)
                    retVal = ReadReg("8203")
                    #					print (ii)
                    # engVal = float(int((retVal[5:8]), 16))

                    # linearize engVal
                    engVal = ((int(retVal[5:8], 16) & 0x3fff) * BIAS_AND_VOLTAGE_RANGES[ii]) / 4096.

                    print(("DAC" + str(ii) + " : " + retVal[5:8]))
                    print(retVal[4] + " : " + retVal[5:8])
                    print("DAC" + str(ii) + " : " + str(engVal))

                    print("#" * 80)
                    print(f"Comparing set value [{last_written_value}] to read value [{str(engVal)}]")
                    if ii == 17 or ii == 16:
                        if not -.25 < engVal < .25:
                            print("Set bias/clock value was outside of acceptable range.")
                            return False


                    elif not (last_written_value - abs(last_written_value * .01) <= engVal
                              and engVal <= last_written_value + abs(last_written_value * .01)):
                        print("Set bias/clock value was outside of acceptable range.")
                        return False
                    print("#" * 80)

                    ii += 1
                elif read_addr == "8201":
                    last_written_value = ((int(read_data, 16) & 0x3fff) * BIAS_AND_VOLTAGE_RANGES[ii]) / 4096.

            file_line = f.readline()

    return True


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
