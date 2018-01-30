#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import time
import datetime
import base64
import json
import threading
import websocket
import serialize


class CoralParallelJob(object):
    """
    Coral Parallel Job
    Apply function to every item of iterable mapper_args and return a list of the results.
    """
    def __init__(self, url):
        """
        :param url: 服务器端地址
        """
        self.url = url
        self.language = 'python'
        self.__map_func = None
        self.__map_args = None
        self.__reduce_func = None
        self.__context = None
        # ----------------------------------
        self.__error = None
        self.__result = {}  # index -> result
        self.__sock = websocket.WebSocket()
        self.__thread = threading.Thread(target=self.__run)
        self.__thread.setDaemon(True)
        self.__time = None
        self.__abort = False
        self.__done = False

    def map(self, func, args, context=None):
        self.__map_func = func
        self.__map_args = args
        self.__context = context
        return self

    def reduce(self, func):
        self.__reduce_func = func
        return self

    def commit(self):
        if self.__time is not None:
            raise Exception('job is already committed')
        self.__time = datetime.datetime.now()
        self.__sock.connect(self.url)
        self.__sock.send(self.__encode())
        self.__thread.start()
        return self

    def __encode(self):
        if not self.__map_func:
            raise Exception('encode job failed: map_func is required')
        if not self.__map_args:
            raise Exception('encode job failed: map_args is required')
        d = {'language': self.language,
             'map_func': serialize.dumps(self.__map_func),
             'map_args': [serialize.dumps(args) for args in self.__map_args],
             'reduce_func': serialize.dumps(self.__reduce_func) if self.__reduce_func else None,
             'context': serialize.dumps(self.__context) if self.__context else None}
        return json.dumps(d)

    # -----------------------------------------------
    def __run(self):
        while not self.__abort and not self.__done:
            try:
                frame = self.__sock.recv()
                if frame == '':
                    self.__error = 'connection is broken'
                    self.__done = True
                    break
                task = json.loads(frame)
                error = task['error']
                if error:
                    self.__error = error
                    self.__done = True
                    break
                task_id = task['task_id']
                result = serialize.loads(task['result'])
                self.__result[task_id] = result
                if self.__reduce_func or len(self.__result) >= len(self.__map_args):
                    self.__done = True
                    break
            except BaseException, e:
                self.__error = 'socket error: %s' % e
                self.__done = True
                break

    def is_done(self):
        return self.__abort or self.__done

    def wait(self, timeout=None):
        self.__thread.join(timeout)

    def wait_interactive(self, interval=1., timeout=-1):
        """interactive wait, printing progress at regular intervals"""
        from IPython.core.display import clear_output, display, display_pretty
        if timeout is None:
            timeout = -1
        tic = time.time()
        while not self.is_done() and (timeout < 0 or time.time() - tic <= timeout):
            self.wait(interval)
            clear_output(wait=True)
            elapsed = (datetime.datetime.now() - self.__time).total_seconds()
            print "%4i/%i tasks finished after %4i s" % (len(self.__result), len(self.__map_args), elapsed)
            sys.stdout.flush()
        print "\ndone"

    def abort(self):
        if not self.is_done():
            self.__abort = True
            self.__sock.close()
            self.__error = 'job is aborted'

    def get(self):
        if self.__error:
            raise Exception(self.__error)
        results = []
        for k in sorted(self.__result.keys()):
            results.append(self.__result[k])
        return results[0] if self.__reduce_func else results

if __name__ == '__main__':
    def f(x):
        return x * 2
    token = '505523f5411846a185bb6151e6c5f358'
    url = "ws://127.0.0.1:5167/parallel?token=%s" % token
    job = CoralParallelJob(url)
    job.map(f, range(10)).commit()
    job.wait_interactive()
    result = job.get()
    print result