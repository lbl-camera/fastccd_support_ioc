#! /usr/bin/python
# -*- coding: utf-8 -*-
from . import cin_constants
from . import cin_register_map
from . import cin_functions
import time

cin_functions.WriteReg(cin_register_map.REG_FCRIC_MASK_REG1, "FFFF", 0)
cin_functions.WriteReg(cin_register_map.REG_FCRIC_MASK_REG2, "FFFF", 0)
cin_functions.WriteReg(cin_register_map.REG_FCRIC_MASK_REG3, "FFFF", 0)
