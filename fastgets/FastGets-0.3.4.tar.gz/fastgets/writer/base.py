# coding: utf8

import os
import csv
import xlrd
import threading
from .. import env
from ..core.errors import WriteError
from ..core.decorators import sync


current_writers = []


class Writer(object):

    def __init__(self, path, columns):

        splits = path.rsplit('/', 1)
        if len(splits) == 2:
            dir_path = splits[0]
            if not os.path.exists(dir_path):
                raise WriteError('目录不存在：{}'.format(dir_path))

        self._path = path
        self._columns = columns
        self._data = []

        current_writers.append(self)

    @sync(threading.Lock())
    def add(self, each):

        # 这里才能确保获取当前的模式
        if env.mode == env.DISTRIBUTED:
            raise WriteError('分布式模式不能使用 writer')

        if not each:
            raise WriteError('添加的数据对象不能为空')
        if isinstance(each, (list, tuple)):
            if len(each) != len(self._columns):
                raise WriteError('添加的数据字段数和定义不一致')
            else:
                self._data.append(each)
        elif isinstance(each, dict):
            unknown_columns = set(each.keys()) - set(self._columns)
            if unknown_columns:
                raise WriteError('以下字段未定义 {}'.format(','.join(list(unknown_columns))))
            self._data.append(
                [
                    each.get(column)
                    for column in self._columns
                ]
            )
        else:
            raise WriteError('添加的数据对象只能是列表或字典类型')

    def save(self):
        pass
