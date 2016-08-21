#!/bin/bash

xrandr --newmode "1368x1024_60.00"  116.52  1368 1456 1600 1832  1024 1025 1028 1060  -HSync +Vsync
xrandr --addmode VIRTUAL1 "1368x1024_60.00"
#xrandr --newmode "1920x1080_60.00"  172.80  1920 2040 2248 2576  1080 1081 1084 1118  -HSync +Vsync
#xrandr --addmode VIRTUAL1 "1920x1080_60.00"
xrandr --output VIRTUAL1 --left-of eDP1
