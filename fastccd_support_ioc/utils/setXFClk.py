#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
from . import cin_constants
from . import cin_register_map
from . import cin_functions
import time

setFreq = str(sys.argv[1])
# print setFreq
print("\n**** Set CIN External FCLK to " + setFreq + "MHz")

if (setFreq == "125"):
    # Set & Enable 125MHz XO
    cin_functions.WriteReg(cin_register_map.REG_FCLK_I2C_DATA_WR, "B000", 0)

elif (setFreq == "200"):
    # Set & Enable 200MHz XO
    cin_functions.WriteReg(cin_register_map.REG_FCLK_I2C_DATA_WR, "7000", 0)

elif (setFreq == "250"):
    # Set & Enable 250MHz XO
    cin_functions.WriteReg(cin_register_map.REG_FCLK_I2C_DATA_WR, "3000", 0)

else:
    print("Invalid FCLK Frequency\n")
    print("Currently only 125MHz, 200MHz and 250MHz are Supported\n")
