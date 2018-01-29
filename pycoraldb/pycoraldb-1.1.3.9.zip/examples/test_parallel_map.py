#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import pycoraldb

import os
import sys

def f(x):
    return x * 2

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5167')
    client.login('pangx', '123321')
    t1 = datetime.datetime.now()
    job = client.map(f, range(5)).commit()
    job.wait_interactive()
    t2 = datetime.datetime.now()
    print t2 - t1
    print job.get()
    print 'over'