#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""
    2018/3/5  WeiYanfeng
    启动 PipePeerServer 。

参考 [36.2. imp — Access the import internals — Python 3.6.4 documentation](https://docs.python.org/3/library/imp.html)
推荐使用 importlib  替代 imp。

其中所需 ppsSettings.py 内容如下：
gDictPipePeerServerParam = {  # PipePeerServer 运行参数
    'sHubIPPort': '39.108.136.173:9110',           # Hub端IP端口号
    'sHubId': '19ae99f03a6eaa51878a4335ec0d06ac',  # Hub端标识
    'sHubPairId': 'MonitHub',                      # Hub端分组标识串
    'sPeerSuffix': 'PipePeer.PythonCTP',           # Peer端访问账号
    'sPeerPasswd': 'zWPDaAArL3',                   # Peer端访问密码
    'iPipePort': 8111,           # PipePeerServer 端守护端口号
    'sPipeHost': '127.0.0.1',    # PipePeerServer 端守护主机IP地址
}

"""

# import _addpath
# import sys
# import time
# from weberFuncs import PrintTimeMsg, LoopPrintSleep, PrettyPrintStr
from pipe.TCmdStringSckP2PLayoutPipe import TCmdStringSckP2PLayoutPipe
from run.RunFuncs import TryToImportSettingsVariable, TimeRunPipePeerServer

#
# def TryToImportSettingsVariable(sSettingsModule, sVariableName):
#     # 动态加载 PipePeerServer 参数配置
#     # from ppsSettings import gDictPipePeerServerParam
#     PrintTimeMsg('TryToImportSettingsVariable.import_module(%s)...' % sSettingsModule)
#     try:
#         p = importlib.import_module(sSettingsModule)
#         # print(dir(p))
#         # dictP = getattr(p, 'gDictPipePeerServerParam')  # p.gDictPipePeerServerParam
#         dictP = getattr(p, sVariableName)
#         PrintTimeMsg('Var(%s)=(%s)' % (sVariableName, PrettyPrintStr(dictP)))
#         return p.gDictPipePeerServerParam
#     except ImportError as e:
#         PrintTimeMsg('TryToImportSettingsVariable.import_module(%s).e=%s!' % (sSettingsModule, str(e)))
#     return None


def TryRunPipePeerServer(sSettingsModule):
    # 尝试启动 PipePeerServer
    dictP = TryToImportSettingsVariable(sSettingsModule, 'gDictPipePeerServerParam')
    if dictP:
        cssa = TCmdStringSckP2PLayoutPipe(
            dictP.get('sHubId', ''),
            dictP.get('sHubIPPort', ''),
            dictP.get('sHubPairId', 'MonitHub'),
            dictP.get('sPeerSuffix', ''),
            dictP.get('sPeerPasswd', ''),
            'PipePeerServer',
            50,
            dictP.get('iPipePort', -1),
            dictP.get('sPipeHost', '127.0.0.1')
        )
        cssa.StartMainThreadLoop()


def RunPipePeerServer(sSettingsModule):
    def cbFunc(sSetModule):
        TryRunPipePeerServer(sSetModule)
    TimeRunPipePeerServer(cbFunc, sSettingsModule)
    # tmBegin = time.time()
    # # TryRunPipePeerServer(sSettingsModule)
    # if time.time() - tmBegin < 10:
    #     LoopPrintSleep(60, 10, 'RunPipePeerServer(%s)Quit' % sSettingsModule)
    # PrintTimeMsg('RunPipePeerServer.(%s)End!' % sSettingsModule)


# def mainRunPipePeerServer(sSettingsTail):
#     RunPipePeerServer(sSettingsTail)
#
# # -------------------------------------
# if __name__ == '__main__':
#     # sSettingsTail = 'ppsSettingsShare'
#     sSettingsModule = 'ppsSettings'
#     mainRunPipePeerServer(sSettingsModule)
