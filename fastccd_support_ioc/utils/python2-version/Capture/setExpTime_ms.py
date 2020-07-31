#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import cin_functions
import cin_register_map

# Convert ms to Hex - 1 count = 10us
exp_time_d = int(float(sys.argv[1])*100)  #inc is 2x CCD clock

if (exp_time_d == 0) :
	exp_time_h = "00000001"
else :
	exp_time_h = str(hex(exp_time_d)).lstrip("0x").zfill(8)
#print exp_time_h
#print exp_time_h[4:]
#print exp_time_h[0:4]

# Write Number of Exposure Time MSB
cin_functions.WriteReg(cin_register_map.REG_EXPOSURETIMEMSB_REG, exp_time_h[0:4], 1)
# Write Number of Exposure Time LSB
cin_functions.WriteReg(cin_register_map.REG_EXPOSURETIMELSB_REG, exp_time_h[4:], 1)
