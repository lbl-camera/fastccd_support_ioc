#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import cin_functions
import cin_register_map

# Convert ms to Hex - 1 count = 20us
time_d = int(float(sys.argv[1]))
# print exp_time_d
if (time_d == 0):
    time_h = "00000001"
else:
    time_h = str(hex(time_d)).lstrip("0x").zfill(8)
# print time_h
# print time_h[4:]
# print time_h[0:4]

# Write Number of Exposure Time MSB
cin_functions.WriteReg(cin_register_map.REG_TRIGGERREPETITIONTIMEMSB_REG, time_h[0:4], 1)
# Write Number of Exposure Time LSB
cin_functions.WriteReg(cin_register_map.REG_TRIGGERREPETITIONTIMELSB_REG, time_h[4:], 1)
