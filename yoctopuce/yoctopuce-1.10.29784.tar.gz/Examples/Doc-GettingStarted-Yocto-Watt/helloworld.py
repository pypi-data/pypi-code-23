#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys

# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..", "..", "Sources"))
from yoctopuce.yocto_api import *
from yoctopuce.yocto_power import *


def usage():
    scriptname = os.path.basename(sys.argv[0])
    print("Usage:")
    print(scriptname + ' <serial_number>')
    print(scriptname + ' <logical_name>')
    print(scriptname + ' any  ')
    sys.exit()


def die(msg):
    sys.exit(msg + ' (check USB cable)')


errmsg = YRefParam()

if len(sys.argv) < 2:
    usage()

target = sys.argv[1]

# Setup the API to use local USB devices
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

if target == 'any':
    # retreive any Power sensor
    sensor = YPower.FirstPower()
    if sensor is None:
        die('No module connected')
else:
    sensor = YPower.FindPower(target + '.power')

if not (sensor.isOnline()):
    die('device not connected')
while sensor.isOnline():
    print("Power :  " + "%2.1f" % sensor.get_currentValue() + "W (Ctrl-C to stop)")
    YAPI.Sleep(1000)
YAPI.FreeAPI()