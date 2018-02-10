# -*- coding: utf-8 -*-
"""interceptor module
"""
from multiprocessing import Process
from Queue import Empty, Full
from socket import AF_INET
import sys
import time


import nfqueue

class Interceptor(object):
    """entrypoint to decide and mangle IP packets
    """

    @classmethod
    def intercept(cls, traffic):
        """initializes egress and ingress packet processes

        :param traffic: egress/ingress class
        :type traffic: Traffic Object
        """

        egress_process = Process(target=run,
                                 args=(traffic.egress_queue, traffic.handle_egress))
        ingress_process = Process(target=run,
                                  args=(traffic.ingress_queue, traffic.handle_ingress))
        log_process = Process(target=log,
                              args=(traffic.error_log, traffic.error_lock))

        egress_process.start()
        ingress_process.start()
        log_process.start()

        egress_process.join()
        ingress_process.join()
        log_process.join()

def run(queue_num, callback):
    """callback entrypoint

    :param queue_num: egress/ingress queue number
    :type queue_num: int

    :param callback: egress/ingress callback function pointer
    :type queue_num: instance method
    """

    queue = nfqueue.queue()
    queue.set_callback(callback)
    queue.fast_open(queue_num, AF_INET)
    #NOTE may be helpful, usefulness unconfirmed
    queue.set_queue_maxlen(65536)

    try:
        print "INITIALIZING: %s" % queue_num
        queue.try_run()
    except KeyboardInterrupt:
        queue.unbind(AF_INET)
        queue.close()

def log(log_queue, log_lock):
    """Continuously looping log function

    :param log_queue: Queue of error info to log to stdout
    :type log_queue: multiprocessing.Queue

    :param log_lock: Lock for streamlining access to log_queue
    :type log_lock: multiprocessing.Lock
    """
    #NOTE using Pool requires same process that created it to call it
    #implementation would be more complicated but would prevent the sleep call
    while True:
        if not log_queue.empty():
            err_str = ''
            #grab queued error data
            with log_lock:
                try:
                    while not log_queue.empty():
                        err_str += log_queue.get_nowait()
                except Full:
                    pass
                except Empty:
                    pass
            #write buffer to stdout
            #TODO change this to logfile flush, not stdout
            print err_str
            sys.stdout.flush()
            #dont sleep before checking again, it's already been long enough
        else:
            #wait until queue is not empty
            time.sleep(0.01) #~10 ms
