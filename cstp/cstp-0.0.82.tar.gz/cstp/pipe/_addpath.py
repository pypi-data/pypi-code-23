#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""    
    2015-04-13  WeiYanfeng
    该单元会自动将上级目录加入到 sys.path 方便于模块间相互引用
"""


def GetThisFilePath(sSubDir=".", sFName=""):
    import os, sys, inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
        os.path.split(inspect.getfile(inspect.currentframe()))[0], sSubDir)))
    if sFName:
        return cmd_subfolder+os.sep+sFName
    return cmd_subfolder


def AddThisFilePath(sSubDir):
    import sys
    cmd_subfolder = GetThisFilePath(sSubDir)
    # print("_init_.cmd_subfolder",cmd_subfolder)
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)


AddThisFilePath('..')
