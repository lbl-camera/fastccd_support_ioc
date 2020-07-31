#! /usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse

# ============================================================================
#               System Constants
# ============================================================================

url = 'http://192.168.1.2/state.xml'
out2_on = 'relay2State=1'

urllib.request.urlopen(url + '?' + out2_on, timeout=0.02)
