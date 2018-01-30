#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5166')
    client.login("test", "123456")
    query = {'bs_flag': u'买入'}
    sort = 'bs_flag,-match_type'
    rs = client.getUserData("pangx.zhiyuan8hao", query=query, sort=sort, offset=1, limit=-1, password="rw8.html")
    print len(rs)
    # import pandas as pd
    # df = pd.DataFrame(rs)
    # print df
