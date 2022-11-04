#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
from fastccd_support_ioc.utils import cin_functions, cin_register_map


def set_exposure_ms(t):
    # Convert ms to Hex - 1 count = 20us
    #if (sys.argv[2] == "200") :
    #       exp_time_d = int(float(sys.argv[1])*50)  #inc is 2x CCD clock
    #else :
    exp_time_d = int(float(t)*32)  #inc is 2x CCD clock
    #print exp_time_d

    if (exp_time_d == 0) :
            exp_time_h = "00000001"
    else :
            exp_time_h = str(hex(exp_time_d)).lstrip("0x").zfill(8)
    # print exp_time_h
    #print exp_time_h[4:]
    #print exp_time_h[0:4]

    # Write Number of Exposure Time MSB
    cin_functions.WriteReg(cin_register_map.REG_EXPOSURETIMEMSB_REG, exp_time_h[0:4], 1)
    # Write Number of Exposure Time LSB
    cin_functions.WriteReg(cin_register_map.REG_EXPOSURETIMELSB_REG, exp_time_h[4:], 1)

def set_exposure_s(t):
    set_exposure_ms(t*1000)
