#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""
    2018/3/6  WeiYanfeng
    启动服务相关函数。

"""

# import _addpath
# import sys
import time
from weberFuncs import PrintTimeMsg, LoopPrintSleep, PrettyPrintStr
import importlib


def TryToImportSettingsVariable(sSettingsModule, sVariableName):
    # 动态加载 PipePeerServer 参数配置
    # from ppsSettings import gDictPipePeerServerParam
    PrintTimeMsg('TryToImportSettingsVariable.import_module(%s)...' % sSettingsModule)
    try:
        p = importlib.import_module(sSettingsModule)
        # print(dir(p))
        # dictP = getattr(p, 'gDictPipePeerServerParam')  # p.gDictPipePeerServerParam
        dictP = getattr(p, sVariableName)
        PrintTimeMsg('Var(%s)=(%s)' % (sVariableName, PrettyPrintStr(dictP)))
        return p.gDictPipePeerServerParam
    except ImportError as e:
        PrintTimeMsg('TryToImportSettingsVariable.import_module(%s).e=%s!' % (sSettingsModule, str(e)))
    return None


def TimeRunPipePeerServer(cbServerFunc, *args, **kwargs):
    tmBegin = time.time()
    cbServerFunc(*args, **kwargs)
    if time.time() - tmBegin < 10:
        LoopPrintSleep(60, 10, 'TimeRunPipePeerServer.ErrorQuit')
    PrintTimeMsg('TimeRunPipePeerServer.End!')

