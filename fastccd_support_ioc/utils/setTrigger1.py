#! /usr/bin/python
# -*- coding: utf-8 -*-
from . import cin_constants
from . import cin_register_map
from . import cin_functions
import time

cin_functions.WriteReg(cin_register_map.REG_TRIGGERMASK_REG, "0001", 0)
