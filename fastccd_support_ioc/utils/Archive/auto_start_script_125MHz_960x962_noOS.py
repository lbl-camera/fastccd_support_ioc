#!/APSshare/epd/rh6-x86_64/bin/python2.7
# -*- coding: utf-8 -*-

import cin_constants
import cin_register_map
import cin_functions
import time
# from epics import caget, caput, cainfo

# cin_functions.setCameraOn()
from epics import caget
from epics import caput
from epics import cainfo

# import subprocess
cin_functions.setCameraOff()
cin_functions.CINPowerDown()

# turn off clocks and bias and put into single mode
caput("FCCD:cam1:fccd_clock_on", 0)
time.sleep(1.0)
caput("FCCD:cam1:fccd_bias_on", 0)
time.sleep(1.0)
caput("FCCD:cam1:ImageMode", "0")

####################
# make sure acopian is power up
# 1 verity power ioc is running?
###results=subprocess.check_output(["pgrep", "-f", "fccd2App"])
# 2 if not running exit
# 3 if running verify that it is powered on
powerStatus = caget('fccd2:WebRelay1:Y0OutB.VAL')
print("Power Supply Status (0=off, 1=on) = " + str(powerStatus))

# power up CIN
cin_functions.CINPowerUp()

##import getCfgFPGAStatus

cin_functions.loadFrmFirmware("/home/user/CVSSandbox/BINARY/CIN_1kFSCCD/top_frame_fpga_r1004.bit")

import getFrmFPGAStatus

# import setFClk ("125")
cin_functions.setFClk("125")
import getFClkStatus

import setFPPowerOn

time.sleep(2)  # Wait to allow visual check
import getPowerStatus

##print "Powering up Acopian power supply for FCCD2 1KFSCCD Detector"
##powerStatus = caget('fccd2:WebRelay1:Y0OutB.VAL')
##print "Power Supply Status (0=off, 1=on) = " + str(powerStatus)
##caput ( 'fccd2:WebRelay1:Y0OutB.VAL' , 1 )
##time.sleep(2.0)

# cin_functions.loadCameraConfigFile("/home/epicsioc/repo/lbl-fastccds-jtw/CameraConfigFiles/a_a_wave_form_960x960j.txt")
# cin_functions.loadCameraConfigFile("/home/epicsioc/repo/lbl-fastccds-jtw/CameraConfigFiles/aa_bias.txt")
time.sleep(2.0)
# cin_functions.loadCameraConfigFile("/home/epicsioc/repo/lbl-fastccds-jtw/CameraConfigFiles/2014_Feb_19-125MHz_CCD_timing_960x962j_noOS_j.txt")
# jtw 7-28-2014 Slight modification to horizontal clocks to make them more symmetrical
cin_functions.loadCameraConfigFile(
    "/home/epicsioc/repo/lbl-fastccds-jtw/CameraConfigFiles/2014_July_28-125MHz_CCD_timing_960x962k_noOS.txt")
time.sleep(1.0)
cin_functions.loadCameraConfigFile(
    "/home/epicsioc/repo/lbl-fastccds-jtw/CameraConfigFiles/2013_Nov_05_Bias_Settings.txt")
time.sleep(1.0)
cin_functions.loadCameraConfigFile(
    "/home/epicsioc/repo/lbl-fastccds-jtw/CameraConfigFiles/2014_Jan_15-125MHz_fCRIC_timing_x8_b.txt")

# first find out if css is running!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Disconnect css
time.sleep(1.0)
caput("FCCD:cam1:fccd_connect_net", 0)

# Set image size
time.sleep(1.0)
caput("FCCD:cam1:SizeX", 960)
time.sleep(1.0)
caput("FCCD:cam1:SizeY", 962)

# Toggle FIFO Size
time.sleep(1.0)
caput("FCCD:cam1:fccd_fifo_size", 5001)
time.sleep(1.0)
caput("FCCD:cam1:fccd_fifo_size", 5000)

# Connect css
time.sleep(1.0)
caput("FCCD:cam1:fccd_connect_net", 1)

# Toggle Descrambling
time.sleep(1.0)
caput("FCCD:cam1:fccd_is_descramble", 0)
time.sleep(1.0)
caput("FCCD:cam1:fccd_is_descramble", 1)

# Set number of images to average for pedistals
time.sleep(1.0)
caput("FCCD:cam1:fccd_frames_pedistal_calc", 1)

# Set STD for thereshold
time.sleep(1.0)
caput("FCCD:cam1:fccd_num_stds", 0)

# If it's running then turn on bias and clocks
time.sleep(1.0)
caput("FCCD:cam1:fccd_bias_on", 1)
time.sleep(1.0)
caput("FCCD:cam1:fccd_clock_on", 1)

# Initialize default settings so that the camera is taking slow images
time.sleep(1.0)
caput("FCCD:cam1:fccd_exp_time", "0.2")
time.sleep(1.0)
caput("FCCD:cam1:fccd_exp_time", "0.1")
time.sleep(1.0)
caput("FCCD:cam1:fccd_cycle_time", "490.0")
time.sleep(1.0)
caput("FCCD:cam1:fccd_cycle_time", "500.0")
##### if we are using imagej no need to turn on display???
#####caput ("FCCD:cam1:fccd_disp_on", "1")
# ImageMode = Continuous
time.sleep(1.0)
caput("FCCD:cam1:ImageMode", "2")
time.sleep(10.0)
cin_functions.setFClk("125")
time.sleep(1.0)
caput("FCCD:cam1:fccd_acq_pedistals", "1")
time.sleep(1.0)
caput("FCCD:cam1:fccd_sub_pedistals", "1")
# can I set contrast?
# or just use image J?

# could do a loop here to make sure there is no fCRIC noise
# 1 draw a box in the middle of the image and do an Analyze->Measure
# 2 look at the STD if it is >500 then go to step 3 else end
# 3 setFClk.py 125
# 4 Go to step 2
#


# print "auto_start_script_fccd2_125MHz.py DONE"
###raw_input("(Press Enter Key to Exit)")
