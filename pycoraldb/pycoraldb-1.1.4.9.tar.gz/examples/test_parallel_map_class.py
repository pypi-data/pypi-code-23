#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb


class Foo(object):
    """"""
    def calc(self, x):
        return x * 2

def f(x):
    foo = Foo()
    return foo.calc(x)

if __name__ == '__main__':
    mr = pycoraldb.CoralParallelClient('coraldb://127.0.0.1:5167')
    mr.login('test', '123456')
    pr = mr.map(f, range(5))
    pr.wait_interactive()
    print pr.get()
    print 'over'