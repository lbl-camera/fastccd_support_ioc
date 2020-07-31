#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time

count = 0
while (count < 1000000):
	import getTempStatus
	count = count + 1
	time.sleep(5)

