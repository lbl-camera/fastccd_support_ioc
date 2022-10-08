#! /usr/bin/python
# -*- coding: utf-8 -*-
from fastccd_support_ioc.utils import cin_constants
from fastccd_support_ioc.utils import cin_register_map
from fastccd_support_ioc.utils import cin_functions
import time

cin_functions.WriteReg(cin_register_map.REG_TRIGGERMASK_REG, "0000", 0)
