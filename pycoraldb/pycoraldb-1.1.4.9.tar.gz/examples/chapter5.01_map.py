#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb

if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5167')
    client.login('test', '123456')
    pr = client.map(lambda x: x * x, range(5)).commit()
    pr.wait_interactive()
    print pr.get()
