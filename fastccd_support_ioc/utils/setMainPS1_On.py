#! /usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse

# ============================================================================
#               System Constants
# ============================================================================

url = 'http://192.168.1.2/state.xml'
out1_on = 'relay1State=1'

print(url + '?' + out1_on)
urllib.request.urlopen(url + '?' + out1_on, timeout=0.02)
