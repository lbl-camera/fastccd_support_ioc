#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import cin_functions
import cin_register_map

# Convert ms to Hex - 1 count = 1ms
cycle_time_d = int(float(sys.argv[1]))  # inc is 2x CCD clock

if (cycle_time_d == 0):
    cycle_time_h = "00000001"
else:
    cycle_time_h = str(hex(cycle_time_d)).lstrip("0x").zfill(8)
# print cycle_time_h
# print cycle_time_h[4:]
# print cycle_time_h[0:4]

# Write Number of Exposure Time MSB
cin_functions.WriteReg(cin_register_map.REG_TRIGGERREPETITIONTIMEMSB_REG, cycle_time_h[0:4], 1)
# Write Number of Exposure Time LSB
cin_functions.WriteReg(cin_register_map.REG_TRIGGERREPETITIONTIMELSB_REG, cycle_time_h[4:], 1)
