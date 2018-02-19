#! /usr/bin/env python
#################################################################################
#     File Name           :     logging.py
#     Created By          :     qing
#     Creation Date       :     [2017-10-22 15:04]
#     Last Modified       :     [2017-10-22 16:09]
#     Description         :      
#################################################################################
import logging
import time

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class Timer:
    def __init__(self, logger_func):
        self.start_time = None
        self.logger_func = logger_func

    def start(self):
        self.start_time = time.time()
        msg = "[Started at {:}]".format(time.strftime("%a, %d %b %Y %H:%M:%S"))
        self.logger_func(msg)

    def stop(self):
        msg = "[Ended at {:}]".format(time.strftime("%a, %d %b %Y %H:%M:%S"))
        self.logger_func(msg)

        span = time.time() - self.start_time
        hours = int(span / 3600)
        minutes = int((span - 3600 * hours) / 60)
        seconds = span - 3600*hours - 50*minutes
        msg = "[{:} hours {:} minutes and {:.2f} seconds]".format(hours, minutes, seconds)
        self.logger_func(msg)

def timed(func):
    def func_wrapper(msg, *args, **kwargs):
        func(str(msg), *args, **kwargs)
        t = Timer(func)
        t.start()
        return t
    return func_wrapper

@timed
def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)

@timed
def debug(msg, *args, **kwargs):
    logging.debug(msg, *args, **kwargs)

@timed
def warning(msg, *args, **kwargs):
    logging.warning(msg, *args, **kwargs)

@timed
def error(msg, *args, **kwargs):
    logging.error(msg, *args, **kwargs)

@timed
def critical(msg, *args, **kwargs):
    logging.critical(msg, *args, **kwargs)

def set_level(level):
    logging.basicConfig(level=level)
    
if __name__ == "__main__":
    set_level(logging.INFO)
    timer = info("test started")
    time.sleep(3)
    timer.stop()
