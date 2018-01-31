# -*- coding: utf8 -*-
import logging
import multiprocessing
import uuid
from multiprocessing import Pool, Semaphore
import os
import signal


def process_worker_init(lock_, parent_id):
    def sig_int(signal_num, frame):
        os.kill(parent_id, signal.SIGSTOP)

    signal.signal(signal.SIGINT, sig_int)
    global process_controller_lock
    process_controller_lock = lock_


class MethodWrapper(object):
    def __init__(self, callable_func, lock):
        self.__callable = callable_func
        self.__lock = lock

    def __call__(self, *args, **kwargs):
        lock = self.__lock or process_controller_lock
        with lock:
            try:
                self.__callable(*args, **kwargs)
            except KeyboardInterrupt:
                pass


class _MultiProcessControlShim(object):
    class MultiShimFuture(object):
        def wait(self):
            pass

    @classmethod
    def execute(cls, method, args, callback=None):
        method(*args)
        if callback is not None:
            callback(None)

        return cls.MultiShimFuture()

    def terminate(self):
        pass

    def close(self):
        pass

    def join(self):
        pass


def get_multi_process_control(processes, use_threads=False):
    if processes == 1:
        return _MultiProcessControlShim()

    return _MultiProcessControl(processes, use_threads=use_threads)


class _MultiProcessControl(object):
    def __use_threads(self, processes):
        from multiprocessing.pool import ThreadPool

        self.__using_threads = True
        self.__processing_pool = ThreadPool(processes)

    def __init__(self, processes=-1, max_pending=-1, use_threads=False):
        processes = multiprocessing.cpu_count() * 2 if processes == -1 else processes
        max_pending_processes = processes * 10 if max_pending == -1 else max_pending
        self.__max_waiting_semaphore = Semaphore(max_pending_processes)
        self.__using_threads = False

        if use_threads:
            self.__use_threads(processes)
        else:
            try:
                self.__processing_pool = Pool(processes, process_worker_init, initargs=(self.__max_waiting_semaphore, os.getpid(),))
            except AssertionError:
                self.__use_threads(processes)

        self.__jobs = {}

    def join(self):
        logging.debug('%s pool joining', self.__class__)
        self.__wait_pending_jobs()
        self.__check_pending_jobs()
        logging.debug('%s pool joined', self.__class__)

    def close(self):
        if self.__processing_pool is not None:
            logging.debug('%s closing & joining pool', self.__class__)
            self.__processing_pool.close()
            self.join()

    def __wait_pending_jobs(self):
        for token, async_result in self.__jobs.items():
            if async_result is not None:
                async_result.wait()

        self.__check_pending_jobs()

    def __check_pending_jobs(self):
        for token, async_result in self.__jobs.items():
            if async_result is not None:
                if not async_result.ready():
                    continue

                async_result.get()
                self.__jobs[token] = None

        self.__jobs = {token: async_result for token, async_result in self.__jobs.items() if async_result is not None}

    def execute(self, method, args, callback=None):
        self.__check_pending_jobs()

        if self.__using_threads:
            method_wrapper_args = (method, self.__max_waiting_semaphore)
        else:
            method_wrapper_args = (method, None)

        token = uuid.uuid4()
        job_async_result = self.__processing_pool.apply_async(
            MethodWrapper(*method_wrapper_args),
            args=args,
            callback=callback)

        self.__jobs[token] = job_async_result

        return job_async_result

    def terminate(self):
        self.__processing_pool.terminate()
        self.__jobs = {}
