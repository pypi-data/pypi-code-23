# coding: utf8

"""
清理者
用来将已经处理过的，早期的文件删掉
"""

import os
import datetime

import constants
from log import logger
import utils


class Cleaner(object):
    directory = None
    unit_fmt = None

    def __init__(self, directory, unit_fmt=None):
        self.directory = directory
        self.unit_fmt = unit_fmt or constants.UNIT_FMT

    def clean(self, keep_seconds):
        """
        保留多久时间以内的
        :param keep_seconds:
        :return: 删掉了多少个文件
        """

        pos_unit_time = None

        pos_file_path = os.path.join(self.directory, constants.POS_FILENAME)
        if os.path.exists(pos_file_path):
            with open(pos_file_path, 'rb') as f:
                pos_data = f.read()
                if pos_data:
                    timestamp, offset = utils.unpack_pos(pos_data)
                    pos_unit_time = datetime.datetime.fromtimestamp(timestamp)

        if not pos_unit_time:
            logger.info('no pos. cannot clean.')
            return 0

        now = datetime.datetime.now()

        num = 0

        for filename in os.listdir(self.directory):
            try:
                unit_time = datetime.datetime.strptime(filename, self.unit_fmt)
                if unit_time + datetime.timedelta(seconds=keep_seconds) < now:
                    # 说明文件要删掉
                    if unit_time < pos_unit_time:
                        # 已经处理过了，可以删掉
                        os.remove(os.path.join(self.directory, filename))
                        num += 1
            except:
                # 说明不是合法的bill文件
                continue

        return num
