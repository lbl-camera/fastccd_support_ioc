#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import cin_functions
import cin_register_map

# Clear the Focus bit
cin_functions.clearFocusBit()

# Get all variables in int format
exp_time_d = int(float(sys.argv[1]) * 32)  # inc is 2x CCD clock
cycle_time_d = int(float(sys.argv[1]) + 100)  # Cycle Time Value
num_exps_d = int(float(sys.argv[2]))  # Number of Exposures to Capture
# Value = 0 will run Continuously

# Convert to 0x0h Format
# Convert ms to Hex - 1 count = 20us
if (exp_time_d == 0):
    exp_time_h = "00000001"
else:
    exp_time_h = str(hex(exp_time_d)).lstrip("0x").zfill(8)
# print exp_time_h
# print exp_time_h[4:]
# print exp_time_h[0:4]

# Cycle Time
cycle_time_h = str(hex(cycle_time_d)).lstrip("0x").zfill(8)

# Number of Exposures
num_exps_h = str(hex(num_exps_d)).lstrip("0x").zfill(4)

# Write Exposure Time MSB
cin_functions.WriteReg(cin_register_map.REG_EXPOSURETIMEMSB_REG, exp_time_h[0:4], 1)
# Write Exposure Time LSB
cin_functions.WriteReg(cin_register_map.REG_EXPOSURETIMELSB_REG, exp_time_h[4:], 1)

# Write Cycle Time MSB
cin_functions.WriteReg(cin_register_map.REG_TRIGGERREPETITIONTIMEMSB_REG, cycle_time_h[0:4], 1)
# Write Cycle Time LSB
cin_functions.WriteReg(cin_register_map.REG_TRIGGERREPETITIONTIMELSB_REG, cycle_time_h[4:], 1)

# Write Number of Exposures and Start triggers
cin_functions.WriteReg(cin_register_map.REG_NUMBEROFEXPOSURE_REG, num_exps_h, 1)

# Set the Focus bit
cin_functions.setFocusBit()

# Start Triggers
cin_functions.WriteReg("8001", "0100", 1)
