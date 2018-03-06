#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""
    2018/2/17  WeiYanfeng
    在P2PLayout模式下，实现IB本地数据采集
"""

# import _addpath
# from . import _addpath
# import sys
from weberFuncs import PrintTimeMsg, GetCurrentTime, PrintAndSleep
from weberFuncs import GetTimeInteger
from peer.TCmdStringSckP2PLayout import TCmdStringSckP2PLayout


# ------------------------------------------------
class TPeerFreqGatherInfo(TCmdStringSckP2PLayout):
    """
    封装定时采集Peer类
    """
    def __init__(self, sHubId, sHostAndPort, sPairId,
                 sSuffix, sAcctPwd, sClientInfo, bVerbosePrintCmdStr=True):
        TCmdStringSckP2PLayout.__init__(
            self, sHubId, sHostAndPort, sPairId, sSuffix, sAcctPwd,
            sClientInfo, bVerbosePrintCmdStr)
        self.dictFreqCallBack = dict()  # 以 sFreqKind 为键值的回调函数

    def DoHandleSendCmdToPeer(self, sSuffixFm,sSuffixTo,sPeerCmd,CmdStr):
        # 返回 True 表示已经处理过
        # if sPeerCmd==CMD3_P2PLAYOUT_SEND_NOTIFY_MAIL:
        #     self.smtp.SendMail(CmdStr[4],CmdStr[5],CmdStr[6],CmdStr[7])
        #     return True
        # else:
        return TCmdStringSckP2PLayout.DoHandleSendCmdToPeer(
            self, sSuffixFm, sSuffixTo, sPeerCmd, CmdStr)

    def RegisterFreqCallBack(self, sFreqKind, sTmMatch, cbFunc):
        """
        :param sFreqKind: 1S,1N,1H,1D
        :param sTmMatch:  时间匹配参数
        :param cbFunc:    回调函数
        :return:
        """
        self.dictFreqCallBack[sFreqKind] = {
            'sTmMatch': sTmMatch,
            'cbFunc': cbFunc,
            'tmLast': GetTimeInteger(),
        }
        PrintTimeMsg('RegisterFreqCallBack(%s,%s)=%s!' % (sFreqKind, sTmMatch, cbFunc))

    def LoopAndProcessLogic(self):
        iLoopCnt = 0
        while not self.gef.IsExitFlagTrue():
            for sFreqKind,dictCB in self.dictFreqCallBack.items():
                bDoCallBack = False
                if sFreqKind == '1S':
                    bDoCallBack = True
                else:
                    sTmMatch = dictCB.get('sTmMatch', '00')
                    tmLast = dictCB.get('tmLast', 0)
                    tmNow = GetTimeInteger()
                    iSecs = tmNow-tmLast
                    sYmdHns = GetCurrentTime()
                    iHalf = 30  #
                    if sFreqKind == '1N':
                        iHalf *= 1
                        if len(sTmMatch) != 2:
                            sTmMatch = '00'
                    if sFreqKind == '1H':
                        iHalf *= 60
                        if len(sTmMatch) != 4:
                            sTmMatch = '0000'
                    elif sFreqKind == '1D':
                        iHalf *= 60*24
                        if len(sTmMatch) != 6:
                            sTmMatch = '080000'
                    if (iSecs >= iHalf*2) or sYmdHns.endswith(sTmMatch):
                        bDoCallBack = True
                if bDoCallBack:
                    cbFunc = dictCB.get('cbFunc', None)
                    if cbFunc:
                        cbFunc(sFreqKind, iLoopCnt)
                        dictCB['tmLast'] = GetTimeInteger()
                    else:
                        PrintTimeMsg('LoopAndProcessLogic(%s).cbFunc=None!' % sFreqKind)
            iLoopCnt += 1
            PrintAndSleep(1, 'LoopAndProcessLogic.iLoopCnt=%d' % iLoopCnt,
                          iLoopCnt % 600 == 1)  # 10分钟打印一次日志

    def SendFreqGatherInfoToMonitor(self, sFreqKind, sDataType, sGatherData):
        self.SendRequestP2PLayoutCmd(
            'Monitor.*',
            ['FreqGather', sFreqKind, GetCurrentTime(), sDataType, sGatherData],
            'sLogicParam',
        )
