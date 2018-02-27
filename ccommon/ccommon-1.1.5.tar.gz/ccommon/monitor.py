#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/30 17:30
# @Author  : chenjw
# @Site    : 
# @File    : monitor.py
# @Software: PyCharm Community Edition
# @Desc    :  do what
import threading
import queue
import time
from ccommon import jsonParse


class ItemCost:
    def __init__(self, min=-1, max=0, count=0, cost=0, ave=0, ms=0):
        self.min = min
        self.max = max
        self.count = count
        self.cost = cost
        self.ave = ave
        self.range = {}
        self.ms = ms

    def addItem(self, num):
        if isinstance(num, int) or isinstance(num, float) and num >= 0:
            if self.min < 0 and num >= 0:
                self.min = num
            elif num < self.min:
                self.min = num
            if num > self.max:
                self.max = num
            self.cost += num
            self.count += 1
            if self.ms > 0:
                range_index = str(int(num / self.ms))
                if range_index not in self.range.keys():
                    self.range[range_index] = 0
                self.range[range_index] += 1

    def loadSum(self):
        if self.count == 0:
            return {'min': 0, 'max': 0, 'count': 0, 'cost': 0, 'ave': 0, 'range': {}}
        else:
            return {'min': self.min, 'max': self.max, 'count': self.count, 'cost': self.cost,
                    'ave': float(self.cost) / float(self.count), 'range': self.range}


class Item():
    def __init__(self, key=None, btime=None, etime=None, cost=None):
        self.key = key
        self.btime = btime
        self.etime = etime
        self.cost = cost


class Monitor():
    def __init__(self, ms=0):
        self.ms = ms
        self._queue = queue.Queue()
        self.lock = threading.Lock()
        self.cost = {}
        self.t = threading.Thread(target=self.syncRecord)
        self.t.start()

    def addItem(self, key, cost):
        self._queue.put(Item(key=key, cost=cost))

    def addItem2(self, key, btime, etime):
        self._queue.put(Item(key=key, btime=btime, etime=etime))

    def syncRecord(self):
        while True:
            if self._queue.empty() is True:
                time.sleep(0.00000001)
            else:
                item = self._queue.get()
                self.recordItem(item)

    def recordItem(self, item):
        self.lock.acquire(1)
        try:
            if item.key is None or (isinstance(item.key, str) and item.key == ''):
                raise
            if item.key not in self.cost.keys():
                self.cost[item.key] = ItemCost(ms=self.ms)
            if item.cost is not None and (isinstance(item.cost, int), isinstance(item.cost, float)):
                self.cost[item.key].addItem(item.cost)
                raise
            if item.btime is not None and (
                    isinstance(item.btime, int), isinstance(item.btime, float)) and item.etime is not None and (
                    isinstance(item.etime, int), isinstance(item.etime, float)) and item.etime >= item.btime:
                self.cost[item.key].addItem(item.etime - item.btime)
                raise
        except:
            pass
        finally:
            self.lock.release()

    def loadRecord(self):
        self.lock.acquire(1)
        ret = {}
        try:
            for k, itemCost in self.cost.items():
                ret[k] = itemCost.loadSum()
        finally:
            self.lock.release()
            return jsonParse.JsonParse(ret)


if __name__ == '__main__':
    m = Monitor(150)
    for i in range(10000):
        m.addItem('key1', 123)
    time.sleep(1)
    print(m.loadRecord().toString())

    pass
