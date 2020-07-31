#!/bin/bash

echo CCD Temp Monitor 
echo Date '\t' SetPoint C  '\t' Sensor C '\t'  Heater Level
c=1
while [ $c -le 1000000 ]
do
#	echo -e '\n'Loop: $c
	'./getTempStatus-notxt.py'
	sleep 60
	((c++))
done
