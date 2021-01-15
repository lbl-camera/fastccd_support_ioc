#! /usr/bin/python
# -*- coding: utf-8 -*-
from . import cin_constants
from . import cin_register_map
from . import cin_functions
import time


def get_voltage(vaddr0, vaddr1, mult, offset, voltage):
    reg_val0 = cin_functions.ReadReg(vaddr0)
    reg_val1 = cin_functions.ReadReg(vaddr1)
    #	print reg_val1[6:8] + reg_val0[4:8]
    #	print int("800000",16)
    reg_val = abs(int(reg_val1[6:8] + reg_val0[4:8], 16) - int("800000", 16))
    #	print reg_val
    voltage = mult * ((0.000000596 * reg_val) + offset)
    #	print voltage
    return voltage


def get_current(iaddr0, iaddr1, current):
    reg_val0 = cin_functions.ReadReg(iaddr0)
    reg_val1 = cin_functions.ReadReg(iaddr1)
    #	print reg_val1[6:8] + reg_val0[4:8]
    reg_val = int(reg_val1[6:8] + reg_val0[4:8], 16)
    reg_val = abs(int("800000", 16) - int(reg_val1[6:8] + reg_val0[4:8], 16))
    #	print reg_val
    current = 0.000000596 * reg_val / 0.003
    #	print current
    return current


# def getPowerStatus():
print(" ")
print("****  CIN Power Monitor  ****")

reg_val = cin_functions.ReadReg(cin_register_map.REG_FPGA_VERSION)
print("CFG FPGA v" + reg_val[4:] + "\n")

reg_val = bin((int(cin_functions.ReadReg(cin_register_map.REG_PS_ENABLE)[4:8], 16)))[2:].zfill(16)
stats_vec = reg_val[:]
if (int(stats_vec[-1]) == 1):

    # ADC == LT4151
    reg_val = cin_functions.ReadReg(cin_register_map.REG_VMON_ADC1_CH1)
    #	print reg_val[4:8]
    voltage = 0.025 * int(reg_val[4:8], 16)
    reg_val = cin_functions.ReadReg(cin_register_map.REG_IMON_ADC1_CH0)
    #	print reg_val[4:8]
    current = 0.00002 * int(reg_val[4:8], 16) / 0.003
    power = voltage * current
    print("V12P_BUS Power  : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # ADC == LT2418
    # V3.3 MGMT
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH50, cin_register_map.REG_VMON_ADC0_CH51, 2, 0.03, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH50, cin_register_map.REG_IMON_ADC0_CH51, current)
    print("V3P3_MGMT Power : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V2.5 MGMT
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH70, cin_register_map.REG_VMON_ADC0_CH71, 2, 0.03, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH70, cin_register_map.REG_IMON_ADC0_CH71, current)
    print("V2P5_MGMT Power : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V1.8 MGMT
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH60, cin_register_map.REG_VMON_ADC0_CH61, 1, 0.00, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH60, cin_register_map.REG_IMON_ADC0_CH61, current)
    print("V1P8_MGMT Power : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V1.2 MGMT
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH20, cin_register_map.REG_VMON_ADC0_CH21, 1, 0.03, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH20, cin_register_map.REG_IMON_ADC0_CH21, current)
    print("V1P2_MGMT Power : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V1.0 ENET
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH30, cin_register_map.REG_VMON_ADC0_CH31, 1, 0.02, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH30, cin_register_map.REG_IMON_ADC0_CH31, current)
    print("V1P0_ENET Power : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V3P3_S3E
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH40, cin_register_map.REG_VMON_ADC0_CH41, 2, 0.03, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH40, cin_register_map.REG_IMON_ADC0_CH41, current)
    print("V3P3_S3E Power  : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V3P3_GEN
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH80, cin_register_map.REG_VMON_ADC0_CH81, 2, 0.015, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH80, cin_register_map.REG_IMON_ADC0_CH81, current)
    print("V3P3_GEN Power  : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V2P5_GEN
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CH90, cin_register_map.REG_VMON_ADC0_CH91, 2, 0.015, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CH90, cin_register_map.REG_IMON_ADC0_CH91, current)
    print("V2P5_GEN Power  : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V0P9_V6
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CHE0, cin_register_map.REG_VMON_ADC0_CHE1, 1, 0.01, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CHE0, cin_register_map.REG_IMON_ADC0_CHE1, current)
    print("V0P9_V6 Power   : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V1P0_V6
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CHB0, cin_register_map.REG_VMON_ADC0_CHB1, 1, 0.04, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CHB0, cin_register_map.REG_IMON_ADC0_CHB1, current)
    print("V1P0_V6 Power   : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V1P2_V6
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CHC0, cin_register_map.REG_VMON_ADC0_CHC1, 1, 0.03, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CHC0, cin_register_map.REG_IMON_ADC0_CHC1, current)
    print("V1P2_V6 Power   : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V2P5_V6
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CHD0, cin_register_map.REG_VMON_ADC0_CHD1, 2, 0.00, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CHD0, cin_register_map.REG_IMON_ADC0_CHD1, current)
    print("V2P5_V6 Power   : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")

    # V_FP
    voltage = get_voltage(cin_register_map.REG_VMON_ADC0_CHF0, cin_register_map.REG_VMON_ADC0_CHF1, 4, 0.03, voltage)
    current = get_current(cin_register_map.REG_IMON_ADC0_CHF0, cin_register_map.REG_IMON_ADC0_CHF1, current)
    print("V_FP Power      : {0:.4s}".format(str(voltage)) + "V @ {0:.5s}".format(str(current)) + "A")
else:
    print("  12V Power Supply is OFF")
