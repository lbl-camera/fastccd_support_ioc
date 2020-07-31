#!/bin/bash

c=1
while [ $c -le 1000000 ]
do
	echo -e '\n'Loop: $c
	'./getTempStatus.py'
	sleep 120
	((c++))
done
