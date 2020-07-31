#! /usr/bin/python
# -*- coding: utf-8 -*-
import cin_constants
import cin_register_map
import cin_functions
import time

cin_functions.WriteReg(cin_register_map.REG_FCRIC_MASK_REG1, "0000", 0)
cin_functions.WriteReg(cin_register_map.REG_FCRIC_MASK_REG2, "0000", 0)
cin_functions.WriteReg(cin_register_map.REG_FCRIC_MASK_REG3, "0000", 0)
