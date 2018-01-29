#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5266')
    # client.login("test", "123456")
    print client.callTs('return 1 * 2;')
    print client.callTs('return getbk("A股");')
