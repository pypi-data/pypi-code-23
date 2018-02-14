#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb
    
if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://192.168.2.150:59020')
    client.login("test", "123456")
    rs = client.getTradingDays()
    print rs
