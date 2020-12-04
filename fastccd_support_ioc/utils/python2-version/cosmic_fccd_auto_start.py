#! /usr/bin/python
# -*- coding: utf-8 -*-

import cin_constants
import cin_register_map
import cin_functions
import time

# Power Cycle CIN to clear stale configurations
cin_functions.CINPowerDown()
cin_functions.CINPowerUp()

import getCfgFPGAStatus

cin_binary_dir = '/home/rp/PycharmProjects/fastccd_support_ioc/fastccd_support_ioc/utils/cin_binary/'
config_dir = '/home/rp/PycharmProjects/fastccd_support_ioc/fastccd_support_ioc/utils/config/'

# Configure Frame FPGA
# jj-changed to lastest fw 05/02/17 In EuXFEL bin location
cin_functions.loadFrmFirmware(cin_binary_dir + "FPGAConfig.bit")

import getFrmFPGAStatus
import setFClk125M
# import setFClk200M
import getFClkStatus

# Load Camera Timing File for 125MHz System Clock
cin_functions.loadCameraConfigFile(config_dir + "TimingConfig.txt")

print
"\nSet Trigger Mux to accept external triggers on FP Trigger Input 1 Only"
import setTrigger0  # Maps to Front Panel Trigger Input 1

# import setTriggerSW

# Set Exposure Time to 1ms
cin_functions.WriteReg("8206", "0000", 1)  # MS Byte
cin_functions.WriteReg("8207", "0032", 1)  # LS Byte
# Set Int TriggerRate to 100ms
cin_functions.WriteReg("8208", "0000", 1)  # MS Byte
cin_functions.WriteReg("8209", "0064", 1)  # LS Byte

# Set Num Exposures == 1
cin_functions.WriteReg("820C", "0001", 1)

# Power up Front Panel boards & FO Modules
import setFPPowerOn

time.sleep(0.2)  # Wait to allow visual check

import set_FOPS_On

time.sleep(0.2)  # Wait to allow visual check

## *********** DO NOT SEND PORT CONNECT ********
#  Send UDP packet to configure Stream Port
# print "\nConfigure CIN for Broadcast Mode Tx"
# import sendConnect

# import getPowerStatus  # Status of CIN internal power supplies
# import getTempStatus
# Can put a test here to check the Sensor Temperature before power on

# raw_input("\n(Press Enter Key to Power Up Camera)")

# Power on Camera
import setMainPS1_On

time.sleep(2)  # Wait to allow visual check
import getCameraPower

cin_functions.loadCameraConfigFile(config_dir + "FCRICConfig.txt")

time.sleep(0.2)  # Wait to allow visual check

cin_functions.loadCameraConfigFile(config_dir + "BiasConfig.txt")

# cin_functions.WriteReg("8204", "0001", 1)
