# coding: utf8

"""
写入者
将记录写入到文件，不处理pos
"""

import os
import datetime
import constants
from bill import Bill

from log import logger


class Writer(object):
    directory = None
    unit_fmt = None

    cur_unit = None
    cur_file = None

    def __init__(self, directory, unit_fmt=None):
        self.directory = directory
        self.unit_fmt = unit_fmt or constants.UNIT_FMT

    def write(self, data):
        """
        写入, 仅支持转换为字符串，因为文件中是以\n换行分割
        :param data:
        :return:
        """

        now = datetime.datetime.now()

        try:
            unit = now.strftime(self.unit_fmt)
            if unit != self.cur_unit and self.cur_file:
                # 说明切换文件了，或者之前没有文件
                self.cur_file.close()
                self.cur_file = None

            if not self.cur_file:
                full_file_path = os.path.join(self.directory, unit)
                full_directory = os.path.dirname(full_file_path)
                if not os.path.exists(full_directory):
                    os.makedirs(full_directory)

                # 字符串模式就行，可读性更好
                self.cur_file = open(full_file_path, 'ab')
                # 打开文件成功之后，才来修改unit
                self.cur_unit = unit

            bill = Bill()

            # 必须是str类型
            if isinstance(data, unicode):
                data = data.encode('utf8')

            bill.body = data

            str_bill = bill.pack()

            self.cur_file.write(str_bill)
            # 强制写入
            self.cur_file.flush()

            return True
        except:
            logger.error('exc occur. data: %r', data, exc_info=True)
            return False
