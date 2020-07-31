#! /usr/bin/python
# -*- coding: utf-8 -*-

import cin_constants
import cin_register_map
import cin_functions
import time

cin_functions.CINPowerDown()
cin_functions.CINPowerUp()

import getCfgFPGAStatus

cin_functions.loadFrmFirmware("/home/user/CVSSandbox/BINARY/CIN_1kFSCCD/top_frame_fpga.bit")

import getFrmFPGAStatus
# import setFClk "200"
# import setFClk125M
import getFClkStatus

import setFPPowerOn

time.sleep(2)  # Wait to allow visual check
import getPowerStatus

print(" ")
input("(Press Enter Key to Exit)")
