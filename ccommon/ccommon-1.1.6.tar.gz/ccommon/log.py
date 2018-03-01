#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/1 10:05
# @Author  : chenjw
# @Site    : 
# @File    : log.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

import logging


def init(logname='log.log'):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logname,
                        filemode='w')


if __name__ == '__main__':
    init()
    logging.info('aa')
    pass
