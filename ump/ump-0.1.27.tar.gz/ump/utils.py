# coding: utf8

import constants
import struct
import fcntl
from fcntl import LOCK_EX, LOCK_SH, LOCK_NB



# 这样pos就是定长的了，不用截断了
def unpack_pos(content):
    return struct.unpack(constants.POS_FMT, content)


def pack_pos(timestamp, offset):
    return struct.pack(constants.POS_FMT, timestamp, offset)


# 加文件锁
def lock_file(file, flags):
    fcntl.flock(file.fileno(), flags)


# 释放文件锁
def unlock_file(file):
    fcntl.flock(file.fileno(), fcntl.LOCK_UN)

