# coding=utf-8
import time


def get_time_stamp():
    return time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
