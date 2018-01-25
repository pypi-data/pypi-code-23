# -*- coding: utf-8 -*-
"""interceptor module
"""
import socket
from multiprocessing import Process

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

        egress_process.start()
        ingress_process.start()

        egress_process.join()
        ingress_process.join()

def run(queue_num, callback):
    """callback entrypoint

    :param queue_num: egress/ingress queue number
    :type queue_num: int

    :param callback: egress/ingress callback function pointer
    :type queue_num: instance method
    """

    queue = nfqueue.queue()
    queue.set_callback(callback)
    queue.open()
    queue.create_queue(queue_num)
    try:
        print "INITIALIZING: %s" % queue_num
        queue.try_run()
    except KeyboardInterrupt:
        queue.unbind(socket.AF_INET)
        queue.close()
