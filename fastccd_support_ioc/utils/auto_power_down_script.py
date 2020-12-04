#! /usr/bin/python
# -*- coding: utf-8 -*-

from fastccd_support_ioc.utils import cin_constants
from fastccd_support_ioc.utils import cin_register_map
from fastccd_support_ioc.utils import cin_functions
import urllib.request, urllib.error, urllib.parse
import time

# import setClocksBiasOff

print("\n Shutting down CCD Bias and Clocks")
cin_functions.setCameraOff()

print("\n Shutting down FO Modules")
from fastccd_support_ioc.utils import set_FOPS_Off

print("\n Shutting down Camera Power Supply")
url = 'http://192.168.1.2/state.xml'
out1_off = 'relay1State=0'
urllib.request.urlopen(url + '?' + out1_off, timeout=0.02)

print("\n Shutting down Camera Interface Node Blade")
cin_functions.CINPowerDown()

# import getCameraPower
print(" ")
