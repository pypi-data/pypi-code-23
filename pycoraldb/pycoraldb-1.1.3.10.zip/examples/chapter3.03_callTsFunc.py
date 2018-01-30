#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5266')
    # client.login("test", "123456")
    ret = client.callTsFunc('co_get_spot_quote', [20180108, 'SH600000'])
    for i, row in enumerate(ret):
        print '[%s/%s] %s' % (i+1, len(ret), row)
        if i > 10:
            break

