#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
from . import cin_functions
from . import cin_register_map

# Convert ms to Hex - 1 count = 10us
# print exp_time_d
exp_time_h = str(hex(int(sys.argv[1]))).lstrip("0x").zfill(8)
# print exp_time_h
# print exp_time_h[4:]
# print exp_time_h[0:4]

# Write Number of Exposure Time MSB
cin_functions.WriteReg(cin_register_map.REG_SHUTTERTIMEMSB_REG, exp_time_h[0:4], 1)
# Write Number of Exposure Time LSB
cin_functions.WriteReg(cin_register_map.REG_SHUTTERTIMELSB_REG, exp_time_h[4:], 1)
