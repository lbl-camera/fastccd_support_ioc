#! /usr/bin/python
# -*- coding: utf-8 -*-

from fastccd_support_ioc.utils import cin_constants
from fastccd_support_ioc.utils import cin_register_map
from fastccd_support_ioc.utils import cin_functions
from fastccd_support_ioc import utils
import time
import os

# Power Cycle CIN to clear stale configurations
cin_functions.CINPowerDown()
cin_functions.CINPowerUp()

from fastccd_support_ioc.utils import getCfgFPGAStatus

# Configure Frame FPGA
# jj-changed to lastest fw 05/02/17 In EuXFEL bin location
cin_functions.loadFrmFirmware(os.path.join(utils.__path__[0], "cin_binary/top_frame_fpga.bit"))
print('firmware loaded')
from fastccd_support_ioc.utils import getFrmFPGAStatus
from fastccd_support_ioc.utils import setFClk125M
# import setFClk200M
from fastccd_support_ioc.utils import getFClkStatus

# Load Camera Timing File for 125MHz System Clock
cin_functions.loadCameraConfigFile(os.path.join(utils.__path__[0], "config/20170525_125MHz_fCCD_Timing_xper.txt"))

# print "\nSet Trigger Mux to accept external triggers on FP Trigger Input 1 Only"
# import setTrigger0   # Maps to Front Panel Trigger Input 1
from fastccd_support_ioc.utils import setTriggerSW

# Set Exposure Time to 1ms
cin_functions.WriteReg("8206", "0000", 1)  # MS Byte
cin_functions.WriteReg("8207", "0032", 1)  # LS Byte
# Set Int TriggerRate to 100ms
cin_functions.WriteReg("8208", "0000", 1)  # MS Byte
cin_functions.WriteReg("8209", "0064", 1)  # LS Byte
# Set Num Exposures == 1
# cin_functions.WriteReg("820C", "0001", 1)
# Power up Front Panel boards
from fastccd_support_ioc.utils import setFPPowerOn

time.sleep(0.2)  # Wait to allow visual check

from fastccd_support_ioc.utils import set_FOPS_On

time.sleep(0.2)  # Wait to allow visual check

#  Send UDP packet to configure Stream Port
# print "\nConfigure CIN for Broadcast Mode Tx"
from fastccd_support_ioc.utils import sendConnect

# import getPowerStatus  # Status of CIN internal power supplies
# import getTempStatus
# Can put a test here to check the Sensor Temperature before power on

# raw_input("\n(Press Enter Key to Power Up Camera)")

# import setMainPS1_On
# time.sleep(2)  # Wait to allow visual check
# import getCameraPower

# raw_input("\n(Press Enter Key to send Bias Configuration to Camera clock board)")

# cin_functions.loadCameraConfigFile("/home/user/CVSSandbox/QT/CINController/config/20140327_XCS_Bias_Settings.txt")

# raw_input("\n(Press Enter Key to send FCRIC Configurations)")

# cin_functions.loadCameraConfigFile("/home/user/CVSSandbox/QT/CINController/config/2013_Nov_25-200_MHz_fCRIC_timing.txt")

# ./setReg.py 8212 00e0 Mask the bad signal lines FCRIC to CIN
# cin_functions.WriteReg("8211", "E000", 1)
# cin_functions.WriteReg("8212", "00E0", 1)

# raw_input("\nfCCD Camera configured and ready to enable (Press Enter Key to Exit)")
# raw_input("\nfCCD Camera ready (Press Enter Key to Exit)")

# "/home/fastCCD/CameraControl/fccd_gui/CIN_Controller"
