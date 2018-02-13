#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/9/4 11:17"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装一些技巧函数。
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from .WyfPublicFuncs import PrintTimeMsg
from .python_version import IsPython3OrLater
import operator
import os


def DictSortByValue(dictVal):
    # 字典按取值排序，返回 [(key,value)] 元组列表
    return sorted(dictVal.items(), key=operator.itemgetter(1))


def DictSortByKey(dictVal):
    # 字典按键排序，返回 [(key,value)] 元组列表
    return sorted(dictVal.items(), key=operator.itemgetter(0))


def TouchFile(fname, times=None):
    """
    生成空文件
    :param fname: 全路径空文件名
    :param times: 如果时间是 None, 则文件的访问和修改设为当前时间。
                  否则, 时间是一个 2-tuple数字, (atime, mtime) 用来分别作为访问和修改的时间。
    :return: 无
    """
    with open(fname, 'a'):
        os.utime(fname, times)


def TryForceMakeDir(sDir):
    # 强制创建目录
    try:
        if IsPython3OrLater():
            os.makedirs(sDir, exist_ok=True)
        else:
            os.makedirs(sDir)
    except OSError as e:
        import errno
        if e.errno != errno.EEXIST:
            PrintTimeMsg('TryForceMakeDir.makedirs(%s).e=%s=' % (sDir, str(e)))


def TryRenameFile(sOldFN, sNewFN):
    # 尝试重命名文件，成功返回 True
    try:
        os.rename(sOldFN, sNewFN)
        return True
    except Exception as e:
        PrintTimeMsg('TryRenameFile(%s,%s).e=%s=' % (sOldFN, sNewFN, str(e)))
        return False


def mainWyfEasyFuncs():
    dictV = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0, 12: 100}
    oRet = DictSortByValue(dictV)
    PrintTimeMsg('DictSortByValue(%s)=%s=' % (dictV, oRet))
    oRet = DictSortByKey(dictV)
    PrintTimeMsg('DictSortByKey(%s)=%s=' % (dictV, oRet))
    # TryForceMakeDir(r'D:\CloudMusic\a\b')
    TryRenameFile(r'D:\CloudMusic\a\b', r'D:\CloudMusic\a\c')


# --------------------------------------
if __name__ == '__main__':
    mainWyfEasyFuncs()
