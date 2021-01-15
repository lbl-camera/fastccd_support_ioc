#! /usr/bin/python
# -*- coding: utf-8 -*-
from . import cin_constants
from . import cin_register_map
from . import cin_functions
import time

# Write to FO Module Register to send Test Pattern
cin_functions.WriteReg("821D", "9E00", 0)
cin_functions.WriteReg("821E", "0000", 0)
cin_functions.WriteReg("821F", "0001", 0)
cin_functions.WriteReg("8001", "0105", 0)

time.sleep(0.2)

cin_functions.WriteReg("8211", "0000", 0)
cin_functions.WriteReg("8212", "0000", 0)
cin_functions.WriteReg("8213", "0000", 0)
