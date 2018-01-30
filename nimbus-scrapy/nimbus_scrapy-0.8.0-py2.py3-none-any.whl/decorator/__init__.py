# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
Package Description
"""
import os
import sys
import logging
import json
from functools import wraps

__all__ = ["singleton", "singleton_", "Singleton",  "Singleton_"]


def singleton(cls):
    """
    Python 官方 wiki 给出了一个非常优雅的实现
    @singleton
    class MyClass(object):
        a = 1
    :param cls: 
    :return: 
    """
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


def singleton_(cls):
    """
    使用装饰器
    我们知道，装饰器（decorator）可以动态地修改一个类或函数的功能。
    这里，我们也可以使用装饰器来装饰某个类，使其只能生成一个实例，
    代码如下：
    @singleton_
    class MyClass(object):
        a = 1
    :param cls: 
    :return: 
    """
    instances = {}

    @wraps(cls)
    def func(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return func


class Singleton(type):
    """
    使用 metaclass
    元类（metaclass）可以控制类的创建过程，它主要做三件事：
    拦截类的创建
    修改类的定义
    返回修改后的类
    使用元类实现单例模式的代码如下：
    # Python2
    class MyClass(object):
        __metaclass__ = Singleton
    # Python3
    class MyClass(metaclass=Singleton):
        pass
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton_(object):
    """
    使用 __new__
    为了使类只能出现一个实例，我们可以使用 __new__ 来控制实例的创建过程，
    代码如下：
    class MyClass(Singleton_):  
        a = 1
    """
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton_, cls).__new__(cls, *args, **kw)
        return cls._instance

