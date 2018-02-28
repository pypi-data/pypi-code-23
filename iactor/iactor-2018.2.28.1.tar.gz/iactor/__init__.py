# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2018-02-28 14:11:34
# @Last Modified 2018-02-28
# @Last Modified time: 2018-02-28 14:42:32

'''
My take on how actors should be implemented for coroutines and functions.
'''

from multiprocessing.pool import ThreadPool
from itertools import cycle
from functools import partial, wraps
from logging import warning
from collections import deque
from math import sqrt
import atexit
from time import sleep
from inspect import isgenerator, isgeneratorfunction
from generators import window, started
from strict_functions import never_parallel


class Actor(object):
    __slots__ = ['fn', 'pools', 'manager']

    def __init__(self, fn, manager):
        assert callable(fn), 'fn needs to be callable'
        assert isinstance(manager, ActorManager), 'manager needs to be a ActorManager'
        self.fn = fn
        self.manager = manager
        self.pools = cycle(self.manager.next_set_of_pools)

    def __call__(self, *args, **kwargs):
        return self.manager(
            partial(self.fn, *args, **kwargs),
            next(self.pools)
        )

    send = __call__ # this is to support coroutine syntax

class ActorManager(dict):
    def __init__(self, thread_count=8, logger=warning):
        dict.__init__(self)
        self.thread_count = thread_count
        self.logger = logger
        self.pools = [ThreadPool(self.threads_per_pool) for _ in range(self.pool_count)]
        #for p in self.pools:
        #    p._taskqueue.maxsize = 2
        self.pool_selector = window(
            cycle(self.pools),
            self.pools_per_actor
        )
        atexit.register(self.finish_tasks)

    @property
    def pools_per_actor(self):
        return int(sqrt(self.thread_count))

    @property
    def threads_per_pool(self):
        return int(sqrt(self.thread_count))

    @property
    def pool_count(self):
        return int(self.thread_count/self.threads_per_pool)

    @staticmethod
    def _run(fn, logger, _hash):
        try:
            return fn(), _hash
        except Exception as ex:
            logger(ex)
            return None, _hash

    def _remove_task(self, task_output):
        actual_output, _hash = task_output
        del self[_hash]
        return actual_output

    def __call__(self, fn, pool):
        _hash = hash(fn) * hash(pool)
        self[_hash] = pool.apply_async(
            self._run,
            (fn, self.logger, _hash),
            callback=self._remove_task
        )
        return self[_hash]

    @property
    def next_set_of_pools(self):
        return next(self.pool_selector)

    def terminate(self):
        for p in self.pools:
            p.terminate()

    def finish_tasks(self):
        while len(self):
            sleep(0.05)
        self.terminate()

    def actor(self, fn):
        ''' this is the main piece used to create new actors for an ActorManager '''
        if isgeneratorfunction(fn):
            # convert generator functions into functions
            # that convert all output generators to Actors
            @wraps(fn)
            def wrapper(*a, **k):
                return self.actor(started(fn)(*a, **k))
            return wrapper
        if isgenerator(fn):
            # grab the send attribute and lock it to single
            # thread because generators are pure sequential
            fn = never_parallel(fn.send)
        return Actor(fn, self)

if __name__ == '__main__':

    print('hi')

    m=ActorManager()

    @m.actor
    def f1(a,b):
        print('f1', locals())

    @m.actor
    def f2(a,b):
        print('f2', locals())
        f1(**locals())
        print('did', locals())

    '''
    for i in range(20):
        f2(i,i+1)
    '''

    '''
    def print_with(a):
        while 1:
            i = yield
            print(a,i)

    printers = [print_with(i) for i in range(10)]
    actors = [m.actor(i) for i in printers]

    print(printers)
    print(actors)

    for a in actors:
        for i in range(10):
            a(i)
    '''
    @m.actor
    def print_with(a):
        while 1:
            i = yield
            print(a,i)
            del i

    printers = deque(map(print_with,range(1000)))

    for p in printers:
        for i in range(10):
            sleep(0.005)
            p(i)
            p.send(i)

    print('done')
