#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.core.cache import cache

from flytrap.base.response import SimpleResponse


def _make_key(func, *args, **kwargs):
    """
    创建key, 保证不会重复
    :param func: 调用者
    :param args: 参数列表
    :param kwargs: 参数字典
    :return:
    """
    str_list = [func.__name__]
    for arg in args:
        str_list.append(getattr(arg, 'name', arg.__class__.__name__))
        str_list.append(getattr(arg, 'id', str(arg)))
    for k, v in kwargs:
        str_list.append(u'_'.join([k, str(v)]))
    return u'_'.join(map(str, str_list))


def cache_response(hour=24):
    """
    缓存响应数据
    :param hour: 天数, 默认一天
    :return:
    """
    timeout = 60 * 60 * hour

    def cache_func(func):
        def cache_results(*args, **kwargs):
            str_key = _make_key(func, *args, **kwargs)
            data = cache.get(str_key)
            if not data:
                response = func(*args, **kwargs)
                data = response.data
                cache.set(str_key, data, timeout=timeout)
            return SimpleResponse(data)

        return cache_results

    return cache_func
