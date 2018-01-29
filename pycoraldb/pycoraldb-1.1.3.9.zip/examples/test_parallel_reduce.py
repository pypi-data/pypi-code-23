#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb


def f_map(x):
    return x * 2

def f_reduce(li):
    return sum(li)

if __name__ == '__main__':
    mr = pycoraldb.CoralParallelClient('coraldb://127.0.0.1:5167')
    mr.login('test', '123456')
    pr = mr.map(f_map, range(5), f_reduce)
    pr.wait_interactive()
    print pr.get()
    print 'over'
