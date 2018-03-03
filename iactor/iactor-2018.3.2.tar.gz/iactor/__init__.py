# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2018-02-28 14:11:34
# @Last Modified 2018-03-02
# @Last Modified time: 2018-03-02 18:09:27

'''
My take on how actors should be implemented for coroutines and functions.
'''

from __future__ import print_function
from collections import deque
from functools import partial, wraps
from inspect import isgenerator, isgeneratorfunction
from itertools import cycle
from logging import exception
from math import sqrt
from multiprocessing.pool import ThreadPool
from threading import Lock
from time import sleep
import atexit
import gc
from generators import window, started
from strict_functions import never_parallel

__all__ = ['ActorManager']

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

class ActorManager(object):
    def __init__(self, thread_count=8, logger=exception):
        self._active_tasks_lock = Lock()
        self.thread_count = thread_count
        self.logger = logger
        self.pools = [ThreadPool(self.threads_per_pool) for _ in range(self.pool_count)]
        self.pool_selector = window(
            cycle(self.pools),
            self.pools_per_actor
        )
        atexit.register(partial(self.finish_tasks, terminate=True))

    @property
    def pools_per_actor(self):
        return int(sqrt(self.thread_count))

    @property
    def threads_per_pool(self):
        return int(sqrt(self.thread_count))

    @property
    def pool_count(self):
        return int(self.thread_count/self.threads_per_pool)

    @property
    def next_set_of_pools(self):
        return next(self.pool_selector)

    @staticmethod
    def _run(fn, logger):
        try:
            fn()
        except Exception as ex:
            logger(ex)

    def __call__(self, fn, pool):
        self.clear_caches()
        pool.apply_async(
            self._run,
            (fn, self.logger)
        )

    def clear_caches(self):
        for p in self.pools:
            p._cache.clear()

    def terminate(self):
        for p in self.pools:
            p.terminate()

    def finish_tasks(self, terminate=False):
        while any(len(p._cache) for p in self.pools) or any(sum((p._inqueue.qsize(), p._outqueue.qsize(), p._taskqueue.qsize())) for p in self.pools):
            sleep(0.1)
        if terminate:
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

    import resource
    mem_usage = lambda:print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    m=ActorManager()

    @m.actor
    def f1(a,b):
        print('f1', locals())

    @m.actor
    def f2(a,b):
        print('f2', locals())
        f1(**locals())
        print('did', locals())


    for i in range(30):
        f2(i,i+1)

    actors = [m.actor(lambda i,x=x:print(i,x)) for x in range(10)]

    mem_usage()
    for a in actors:
        for i in range(10):
            a(i)
    mem_usage()

    # recursion also plays nicely with actors

    @m.actor
    def count_to_10000(starting_at):
        if starting_at<10000:
            mem_usage()
            print(starting_at)
            count_to_10000(starting_at+1)

    #count_to_10000(0)
    m.finish_tasks()
    print('done')
    mem_usage()
