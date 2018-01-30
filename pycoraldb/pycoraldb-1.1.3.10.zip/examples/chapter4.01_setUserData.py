#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5166')
    client.login("test", "123456")
    data = {'code': '60000.SH', 'price': 1.234, 'volume': 100, 'enabled': True}
    rs = client.setUserData("test", data)
    print rs
