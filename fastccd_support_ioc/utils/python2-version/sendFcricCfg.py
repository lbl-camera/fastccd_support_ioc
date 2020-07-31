#! /usr/bin/python
# -*- coding: utf-8 -*-

import cin_constants
import cin_register_map
import cin_functions
import time

cin_functions.loadCameraConfigFile("/home/user/CVSSandbox/QT/CINController/config/2013_Nov_25-200_MHz_fCRIC_timing.txt")

# ./setReg.py 8212 00e0 Mask the bad signal lines FCRIC to CIN
cin_functions.WriteReg("8211", "E000", 1)
cin_functions.WriteReg("8212", "00E0", 1)

raw_input("\nConfiguration Data sent to all fCRICs  (Press Enter Key to Exit)")
