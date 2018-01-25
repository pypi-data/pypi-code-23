# coding: utf8

"""
检查pos是否在合理的时间范围内
"""

import os
import datetime
import constants
from log import logger
import utils


class Checker(object):

    directory = None
    unit_fmt = None

    def __init__(self, directory, unit_fmt=None):
        self.directory = directory
        self.unit_fmt = unit_fmt or constants.UNIT_FMT

    def check(self, safe_seconds):
        """
        检查，unit离现在多久之内是安全的
        :param safe_seconds:
        :return:
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
            logger.info('no pos')
            return True
        else:
            now = datetime.datetime.now()
            if pos_unit_time + datetime.timedelta(seconds=safe_seconds) < now:
                # 说明pos已经太久没有移动了
                logger.error('pos is too old. pos_unit_time: %s, now: %s', pos_unit_time, now)
                return False
            else:
                return True

