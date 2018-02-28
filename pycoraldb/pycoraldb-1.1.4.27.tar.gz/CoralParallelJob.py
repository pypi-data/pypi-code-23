#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import time
import datetime
import json
import threading
import websocket
import serialize
import compress
import progressbar


class CoralParallelJob(object):
    """
    Coral Parallel Job
    Apply function to every item of iterable mapper_args and return a list of the results.
    """
    def __init__(self, url):
        """
        :param url: 服务器端地址
        """
        self.enable_output = True
        self.url = url
        self.language = 'python'
        self.__map_func = None
        self.__map_args = None
        self.__reduce_func = None
        self.__context = None
        # ----------------------------------
        self.__error = None
        self.__map_results = {} # index -> result
        self.__reduce_results = {}  # index -> result
        self.__sock = websocket.WebSocket()
        self.__thread = threading.Thread(target=self.__run)
        self.__thread.setDaemon(True)
        self.__time = None
        self.__status = ''
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
             'context': serialize.dumps(self.__context) if self.__context else None,
             'enable_output': self.enable_output}
        data = json.dumps(d)
        data = compress.smart_compress_gzip(data)
        return data

    def __run(self):
        try:
            self.__status = 'Connecting ...'
            self.__sock.connect(self.url)
            self.__status = 'Preparing ...'
            req = self.__encode()
            self.__status = 'Committing ...'
            self.__sock.send(req)
        except BaseException, e:
            self.__error = 'error: %s' % e
            self.__done = True
            self.__status = 'Failed'
        while not self.__abort and not self.__done:
            try:
                frame = self.__sock.recv()
                if self.is_done():
                    break
                if not frame:
                    self.__error = 'connection is broken'
                    self.__done = True
                    break
                frame = compress.smart_uncompress_gzip(frame)
                msg = json.loads(frame)
                function_id = msg['function_id']
                if function_id not in [2, 4, 5, 6]:
                    sys.stdout.write('unknown message received: %s\n' % msg)
                    continue
                if function_id == 5:
                    self.__status = msg['status']
                elif function_id == 6:
                    if self.enable_output:
                        output = msg['output']
                        sys.stdout.write(output)
                else:
                    if self.enable_output:
                        output = msg['output']
                        if output:
                            sys.stdout.write(output)
                    index = msg['index']
                    error = msg['error']
                    if error:
                        pretty_error = error
                        if function_id == 2:
                            pretty_error = 'map task[%s] error: %s' % (index, error)
                        elif function_id == 4:
                            pretty_error = 'reduce task error: %s' % error
                        self.__error = pretty_error
                        self.__done = True
                        self.__status = 'Failed'
                        break
                    result = serialize.loads(msg['result']) if msg['result'] else None
                    if function_id == 2:
                        self.__map_results[index] = result
                    elif function_id == 4:
                        self.__reduce_results[index] = result
                    if (not self.__reduce_func and len(self.__map_results) >= len(self.__map_args)) or \
                            (self.__reduce_func and len(self.__reduce_results) > 0):
                        self.__done = True
                        self.__status = 'Finished'
                        break
            except BaseException, e:
                self.__error = 'error: %s' % e
                self.__done = True
                self.__status = 'Failed'
                break

    def is_done(self):
        return self.__abort or self.__done

    def wait(self, interactive=True, timeout=None):
        """interactive wait, printing progress at regular intervals"""
        if not interactive:
            try:
                self.__thread.join(timeout)
            except KeyboardInterrupt:
                self.__error = 'aborted by user'
                self.__abort = True
                self.__status = 'Aborted'
                self.__sock.shutdown()
        else:
            tic = time.time()
            total = len(self.__map_args) + 1 if self.__reduce_func else len(self.__map_args)
            bar = progressbar.ProgressBar(total=total)
            bar.start()
            try:
                while not self.is_done() and (timeout is None or time.time() - tic <= timeout):
                    self.__thread.join(1.0)
                    count = (len(self.__map_results) + len(self.__reduce_results))
                    bar.set_msg(self.__status, refresh=False)
                    bar.update(count)
            except KeyboardInterrupt:
                self.__error = 'aborted by user'
                self.__abort = True
                self.__status = 'Aborted'
                self.__sock.shutdown()
            finally:
                bar.set_msg(self.__status, refresh=True)
                bar.close()

    def abort(self):
        if not self.is_done():
            self.__abort = True
            self.__sock.close()
            self.__error = 'job is aborted'
            self.__status = 'Aborted'

    def get(self):
        if self.__error:
            raise Exception(self.__error)
        ret = None
        if self.__reduce_func:
            if self.__reduce_results:
                ret = self.__reduce_results.values()[0]
        else:
            ret = []
            for k in sorted(self.__map_results.keys()):
                ret.append(self.__map_results[k])
        return ret


if __name__ == '__main__':
    def f(x):
        return x * 2
    token = '505523f5411846a185bb6151e6c5f358'
    url = "ws://127.0.0.1:5167/parallel?token=%s" % token
    job = CoralParallelJob(url)
    job.map(f, range(10)).commit()
    job.wait()
    result = job.get()
    print result