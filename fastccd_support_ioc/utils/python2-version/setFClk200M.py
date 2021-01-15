#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import cin_constants
import cin_register_map
import cin_functions
import time

print
"\n**** Set CIN External FCLK to 200MHz"

# Set & Enable 200MHz XO
cin_functions.WriteReg(cin_register_map.REG_FCLK_I2C_DATA_WR, "7000", 0)
