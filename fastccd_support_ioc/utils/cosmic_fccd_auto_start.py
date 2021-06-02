#! /usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import cin_constants
import cin_register_map
import cin_functions
import time
from caproto.sync.client import write

# TODO: Add these checks:
# Front panel boards:
# 4.3 to 4.7 V
# No check on current for now
# Check voltages with +-.2 V ranges from getCameraPower.py

# Power Cycle CIN to clear stale configurations
from fastccd_support_ioc.utils.protection_checks import check_FOPS, check_camera_power, temp_check

# temp_check()

cin_functions.CINPowerDown()
cin_functions.CINPowerUp()

import getCfgFPGAStatus

cin_binary_dir = '/home/rp/PycharmProjects/fastccd_support_ioc/fastccd_support_ioc/utils/cin_binary/'
config_dir = '/home/rp/PycharmProjects/fastccd_support_ioc/fastccd_support_ioc/utils/config/'

# Configure Frame FPGA
# jj-changed to lastest fw 05/02/17 In EuXFEL bin location
cin_functions.loadFrmFirmware(cin_binary_dir + "FPGAConfig.bit")  # TODO: symlink to 302D

import getFrmFPGAStatus
import setFClk125M
# import setFClk200M
import getFClkStatus

# Load Camera Timing File for 125MHz System Clock
cin_functions.loadCameraConfigFile(config_dir + "TimingConfig.txt")

print("\nSet Trigger Mux to accept external triggers on FP Trigger Input 1 Only")
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

# Don't power up (for testing)
print(subprocess.run(['systemctl', 'restart', 'epics.service'], capture_output=True, text=True, check=True))
time.sleep(10)
write('ES7011:FastCCD:cam1:Acquire', 1)  # always necessary after restart
write('ES7011:FastCCD:cam1:OverscanCols', 0)  # maybe only necessary in test frame mode
exit(0)

temp_check()

# Power up Front Panel boards & FO Modules
import setFPPowerOn

time.sleep(0.2)  # Wait to allow visual check

import set_FOPS_On

time.sleep(.2)

if not check_FOPS():
    import auto_power_down_script
    raise ValueError('The FOPS values were outside acceptable range. The camera has been powered down.')

## *********** DO NOT SEND PORT CONNECT ********
#  Send UDP packet to configure Stream Port
# print "\nConfigure CIN for Broadcast Mode Tx"
# import sendConnect

# import getPowerStatus  # Status of CIN internal power supplies
# import getTempStatus
# Can put a test here to check the Sensor Temperature before power on

# input("\n(Press Enter Key to Power Up Camera)")

# Power on Camera
import setMainPS1_On

time.sleep(2)  # Wait to allow visual check

if not check_camera_power():
    import auto_power_down_script
    raise ValueError('The camera power values were outside an acceptable range. The camera has been powered down.')

# input("\n(Press Enter Key to Continue)")

cin_functions.loadCameraConfigFile(config_dir + "FCRICConfig.txt")

time.sleep(0.2)  # Wait to allow visual check

from fastccd_support_ioc.utils.sendBiasConfig import sendBiasConfig

if not sendBiasConfig(config_dir + "BiasConfig.txt"):
    import auto_power_down_script

    raise ValueError(
        'The camera bias/clock readback values were outside an acceptable range. The camera has been powered down.')

temp_check()

import setClocksBiasOn

print(subprocess.run(['systemctl', 'restart', 'epics.service'], capture_output=True, text=True, check=True))

time.sleep(10)
try:
    write('ES7011:FastCCD:cam1:Acquire', 1)  # always necessary after restart
    write('ES7011:FastCCD:cam1:OverscanCols', 0)  # maybe only necessary in test frame mode
except Exception as e:
    raise RuntimeError("Setting Acquire / OverscanCols failed") from e

if __name__ == "__main__":
    pass
