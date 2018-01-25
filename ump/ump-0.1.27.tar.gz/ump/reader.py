# coding: utf8

"""
读取者
将记录从文件中一条条的取出来，并移动pos
"""

from fcntl import LOCK_EX, LOCK_SH, LOCK_NB
import os
import time
import datetime
import constants
from log import logger
from bill import Bill
import utils


class Reader(object):
    directory = None
    unit_fmt = None
    unit_interval = None
    bill_read_chunk_size = None

    cache_unit_file = None

    pos_file = None
    # index是下次fetch需要使用的行号，即使文件不存在，那初始化的index=0即可
    # dict(unit='2018011001', index=None)
    pos_unit_time = None
    pos_offset = None

    pos_file_locked = False

    def __init__(self, directory, unit_fmt=None, unit_interval=None, bill_read_chunk=None):
        self.directory = directory
        self.unit_fmt = unit_fmt or constants.UNIT_FMT
        self.unit_interval = unit_interval or constants.UNIT_INTERVAL
        self.bill_read_chunk_size = bill_read_chunk or constants.BILL_READ_CHUNK_SIZE

        self._prepare_pos_file()

    def __del__(self):
        if self.pos_file_locked and self.pos_file:
            try:
                utils.unlock_file(self.pos_file)
            except:
                logger.error('unlock file fail.', exc_info=True)

    def fetch(self, end_unit_time=None, init_unit_time=None):
        """
        拉取一条数据
        :param end_unit_time: 闭区间
        :param init_unit_time: 闭区间
        :return:
        """

        if not self.pos_file_locked:
            raise Exception('pos file not locked')

        now = datetime.datetime.now()
        # 如果 end_unit_time 不传入的话，就使用上个interval
        if not end_unit_time:
            end_unit_time = datetime.datetime.strptime(
                (now - datetime.timedelta(**self.unit_interval)).strftime(self.unit_fmt),
                self.unit_fmt
            )

        # 可以强制指定开始时间，但是仅当pos没有记录时有效
        # 否则就会设置为和end_unit_time一样
        if not init_unit_time:
            init_unit_time = end_unit_time

        if self.pos_unit_time is None:
            # 说明第一次生成
            self.pos_unit_time = init_unit_time
            self.pos_offset = 0

        if self.pos_unit_time > end_unit_time:
            # 已经超过了end_unit_time
            logger.debug('post_unit_time: %s, end_unit_time: %s', self.pos_unit_time, end_unit_time)
            return None

        while True:
            # 从pos开始的文件开始寻找
            unit = self.pos_unit_time.strftime(self.unit_fmt)
            full_file_path = os.path.join(self.directory, unit)
            full_directory = os.path.dirname(full_file_path)

            if not os.path.exists(full_directory):
                os.makedirs(full_directory)

            if os.path.exists(full_file_path):
                # 文件存在
                if self.cache_unit_file and self.cache_unit_file.name != full_file_path:
                    # 说明要重新创建了
                    self.cache_unit_file.close()
                    self.cache_unit_file = None

                if not self.cache_unit_file:
                    self.cache_unit_file = open(full_file_path, 'rb')

                bill = Bill()

                read_buf = ''

                # 因为可能会出现读取一次没有读完的情况，所以需要做二次seek，但是此时的pos不能写入到pos文件，因为这时的pos不是一个合法的开始地址
                seek_offset = self.pos_offset

                # 尝试读取
                while True:
                    # 偏移到该位置
                    self.cache_unit_file.seek(seek_offset)

                    chunk = self.cache_unit_file.read(self.bill_read_chunk_size)
                    if not chunk:
                        # 说明已经没有数据了
                        # 跳出读取这个文件的循环，去尝试下一个文件
                        break

                    read_buf += chunk

                    ret = bill.check(read_buf)
                    if ret < 0:
                        # 说明内容错误
                        logger.error('invalid read_buf. read_buf: %r', read_buf)
                        # 把这部分内容直接放弃，否则没法继续了
                        read_buf = ''
                        seek_offset += len(chunk)
                        self.pos_offset = seek_offset
                        self._save_pos_file()
                    elif ret > 0:
                        # 收到一条完整的了
                        bill.unpack(read_buf)

                        remain_size = len(read_buf) - ret
                        seek_offset += len(chunk) - remain_size

                        self.pos_offset = seek_offset
                        # 保存下一个位置
                        self._save_pos_file()

                        return bill.body
                    else:
                        # 一次没有读取完
                        seek_offset += len(chunk)
                        # 继续读取，read_buf要继续用
                        continue

                # 如果整个文件跑完了，都没有发现
                # 那就继续找下一个呗

            if self.pos_unit_time + datetime.timedelta(**self.unit_interval) > end_unit_time:
                # 已经超过了时间了
                logger.debug('post_unit_time: %s, end_unit_time: %s', self.pos_unit_time, end_unit_time)
                return None
            else:
                self.pos_unit_time += datetime.timedelta(**self.unit_interval)
                self.pos_offset = 0
                self._save_pos_file()
                # 继续下一个循环

    def _prepare_pos_file(self):
        pos_file_path = os.path.join(self.directory, constants.POS_FILENAME)
        if not os.path.exists(pos_file_path):
            # 文件不存在
            pos_directory = os.path.dirname(pos_file_path)
            if not os.path.exists(pos_directory):
                os.makedirs(pos_directory)

            with open(pos_file_path, 'wb') as f:
                # 创建出来
                pass

        # 读写模式，并且不会清空内容
        self.pos_file = open(pos_file_path, 'rb+')

        try:
            # 锁失败会抛出异常
            utils.lock_file(self.pos_file, LOCK_EX|LOCK_NB)
            self.pos_file_locked = True
        except Exception, e:
            logger.error('pos file lock fail.', exc_info=True)
            raise e

        pos_data = self.pos_file.read()
        if pos_data:
            timestamp, offset = utils.unpack_pos(pos_data)

            self.pos_unit_time = datetime.datetime.fromtimestamp(timestamp)
            self.pos_offset = offset

    def _save_pos_file(self):

        timestamp = time.mktime(self.pos_unit_time.timetuple())
        offset = self.pos_offset

        # 清空
        # 一定要seek，否则write多次会报错
        self.pos_file.seek(0)
        self.pos_file.write(utils.pack_pos(timestamp, offset))
        self.pos_file.flush()
