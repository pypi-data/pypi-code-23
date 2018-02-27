# -*- coding: utf-8 -*-
from ladon.types.ladontype import LadonType
from ladon.compat import PORTABLE_BYTES
import ladon.tools.log as log
import inspect
import time
from ladon.tools.processmanagement import ManagedProcess, MultiProcessTaskContext
from ladon.tools.threadmanagement import ManagedThread, ThreadedTaskContext
from ladon.exceptions.service import ServerFault
try:
    import memcache
    import redis
except:
    pass


task_id_type = {
    'type': PORTABLE_BYTES,
    'doc': u'unique hash identifying the task to that has been created'
}


class TaskInfoResponse(LadonType):
    task_id = task_id_type


class TaskProgressResponse(LadonType):
    task_id = task_id_type
    progress = {
        'type': float,
        'doc': u'Floating point value between 0 and 1 denoting the progress in percent'
    }
    duration = {
        'type': float,
        'doc': u'Floating point value that informs how long time in seconds the task as run'
    }
    starttime = {
        'type': float,
        'doc': u'The start time in seconds since the epoch as a floating point number'
    }


taskProgress_args = (PORTABLE_BYTES,)
taskProgress_kw = {
    'rtype': TaskProgressResponse
}


class ThreadedTaskRunner(ManagedThread):
    def __init__(self, method, args, kw):
        self.method = method
        self.args = args
        self.kw = kw
        super(ThreadedTaskRunner, self).__init__()

    def run_managed(self):
        argspecs = inspect.getargspec(self.method)
        try:
            if argspecs.keywords != None:
                res = self.method(*(self.args), **(self.kw))
            else:
                res = self.method(*(self.args))
            self.set_task_info('result', res)
        except Exception as e:
            self.set_task_info('exception', log.get_traceback())
            log.write("Thread ID: %s (%s) failed with the following exception:\n%s" % (
                self.task_id, self.__class__, log.get_traceback()))
            raise


class MultiProcessTaskRunner(ManagedProcess):
    def __init__(self, cache_client, method, args, kw):
        self.method = method
        self.args = args
        self.kw = kw
        super(MultiProcessTaskRunner, self).__init__(cache_client)

    def run_managed(self):
        argspecs = inspect.getargspec(self.method)
        try:
            if argspecs.keywords != None:
                res = self.method(*(self.args), **(self.kw))
            else:
                res = self.method(*(self.args))
            if inspect.getmro(res.__class__).count(LadonType):
                self.set_task_info('result', res.__dict__(self.kw.get('LADON_METHOD_TC')))
            else:
                self.set_task_info('result', res)
        except Exception as e:
            self.set_task_info('exception', log.get_traceback())
            log.write("Process ID: %s (%s) failed with the following exception:\n%s" % (
                self.task_id, self.__class__, log.get_traceback()))
            raise


def lookup_cache_server(kw):

    """
    Check if this is a multiprocessing task with cache server attached
    """
    cache_client = None
    memcache_server = kw.get('LADON_TASKTYPE_MEMCACHE_SERVER', None)
    if memcache_server:
        port = 11211
        cache_client = memcache.Client(['{}:{}'.format(memcache_server, port)], debug=0)
    else:
        redis_server = kw.get('LADON_TASKTYPE_REDIS_SERVER', None)
        if redis_server:
            port = 6379
            pool = redis.ConnectionPool(host=redis_server, port=port, db=0)
            cache_client = redis.Redis(connection_pool=pool)
    return cache_client


def task_starter(self, *args, **kw):
    cache_client = lookup_cache_server(kw)
    task_method = getattr(self, "_task_%s" % kw['LADON_METHOD_NAME'])
    if cache_client:
        tr = MultiProcessTaskRunner(cache_client, task_method, args, kw)
    else:
        tr = ThreadedTaskRunner(task_method, args, kw)
    kw['update_progress'] = tr.update_progress
    tr.start()
    tir = TaskInfoResponse()
    tir.task_id = tr.task_id
    return tir


def task_progress(self, task_id, **kw):
    cache_client = lookup_cache_server(kw)
    if cache_client:
        context = MultiProcessTaskContext(cache_client, task_id)
    else:
        context = ThreadedTaskContext(task_id)
    tpr = TaskProgressResponse()
    tpr.task_id = task_id
    tpr.progress = context.get_task_info('progress')
    if tpr.progress == None:
        raise ServerFault("Task ID: %s does not seem to exist" % task_id)
    tpr.starttime = context.get_task_info('start')
    stoptime = context.get_task_info('stop')
    tpr.duration = (stoptime if stoptime else time.time()) - tpr.starttime
    return tpr


def task_result(self, task_id, **kw):
    cache_client = lookup_cache_server(kw)
    if cache_client:
        context = MultiProcessTaskContext(cache_client, task_id)
    else:
        context = ThreadedTaskContext(task_id)
    exc = context.get_task_info('exception')
    if exc:
        context.remove_task_info('exception')
        raise ServerFault(
            "Error occured while executing task_id: %s" % task_id, exc)
    res = context.get_task_info('result')
    if res:
        context.remove_task_info('result')
        typ = kw.get('LADON_RTYPE')
        if inspect.getmro(typ).count(LadonType):
            return typ(prime_dict=res, tc=kw.get('LADON_METHOD_TC'), export_dict=kw)
        else:
            return res
    else:
        if context.task_running():
            raise ServerFault(
                "Task ID: %s has no result because it is still running" % task_id)
        else:
            raise ServerFault(
                "Task ID: %s has no result and is not running either. Probably the result has already been fetched" % task_id)
