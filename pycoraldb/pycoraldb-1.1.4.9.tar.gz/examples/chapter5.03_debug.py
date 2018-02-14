#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pycoraldb
import time

def test_debug_in_map(task):
    result = task['x'] * task['y']
    print 'calc task: id = %s, x = %s, y = %s, result = %s' % (task['id'], task['x'], task['y'], result)
    return result


def test_debug_in_reduce(results):
    print 'in reduce'
    return 100
    ret = 0
    for result in results:
        ret += result
    print 'do sum over, results = %s, sum = %s' % (results, ret)
    return ret


if __name__ == '__main__':
    # client = pycoraldb.CoralDBClient('coraldb://192.168.2.150:59020')
    client = pycoraldb.CoralDBClient('coraldb://127.0.0.1:5266')
    client.login('test', '123456')
    tasks = []
    tasks.append({'id': 'task1', 'x': 1, 'y': 2})
    # tasks.append({'id': 'task2', 'x': 3, 'y': 4})
    # tasks.append({'id': 'task3', 'x': 5, 'y': 6})
    # tasks.append({'id': 'task3', 'x': 5, 'y': 6})
    # tasks.append({'id': 'task3', 'x': 5, 'y': 6})
    # tasks.append({'id': 'task3', 'x': 5, 'y': 6})
    # tasks.append({'id': 'task3', 'x': 5, 'y': 6})
    # tasks.append({'id': 'task3', 'x': 5, 'y': 6})
    # pr = client.map(test_debug_in_map, tasks).reduce(test_debug_in_reduce).commit()
    pr = client.map(test_debug_in_map, tasks).reduce(test_debug_in_reduce).commit()
    pr.wait()
    print pr.get()
