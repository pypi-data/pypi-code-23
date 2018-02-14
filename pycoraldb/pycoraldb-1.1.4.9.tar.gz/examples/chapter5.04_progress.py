#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb
import time

import time
def test_monitor(task):
    #print "I'am the %sth task, I will sleep for %ss ......" % (task['i'], task['sleep'])
    time.sleep(task['sleep'])
    #print "I'am the %sth task, I woke up and continued to work." % (task['i'])
    # 这里演示没有返回值的map函数
    # return None


if __name__ == '__main__':
    client = pycoraldb.CoralDBClient('coraldb://192.168.2.150:59020')
    # client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5266')
    client.login('test', '123456')
    tasks = []
    for i in xrange(10):
        tasks.append({'i': i, 'sleep': i % 3 + 5})
    pr = client.map(test_monitor, tasks).commit()
    print 'start wait'
    pr.wait()
    print pr.get()
