#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 15:30:12 2017

@author: chernov
"""

DEF_RSH_PARAMS = {
    "filepath": "this",
    "num_blocks": 0,
    "aquisition_time": 1.0e+4,
    "blocks_in_file": -1,
    "waitTime": 1e+3,
    "threshold": 0.1,
    "synchro_control": ["FrequencySwitchOff", "SlopeFront"],
    "synchro_channel": {
        "type": "SYNCHRO_PROGRAMM",
        "params": ["Default"],
        "gain": 1
    },
    "sample_freq": 3.125e+6,
    "pre_history": 8,
    "packet_number": 1,
    "b_size": 1048576,
    "channel_number": 1,
    "hysteresis": 0,
    "channel": [
        {
            "params": ["Used", "Synchro", "Resist50Ohm"],
            "adjustment": 0,
            "gain": 1
        },
        {
            "params": ["NotUsed"],
            "adjustment": 0,
            "gain": 1
        }
    ]
}
