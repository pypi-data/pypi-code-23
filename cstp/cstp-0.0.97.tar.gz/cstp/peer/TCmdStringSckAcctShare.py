# -*- coding:utf-8 -*-
"""
Created on 2016-6-30
@author: WeiYanfeng

从 TCmdStringSck 继承，实现 AcctShare 的客户端。

"""
# import _addpath
from . import _addpath
import sys
from weberFuncs import PrintTimeMsg, GetCurrentTime, PrintAndSleep
from cpyf.mGlobalConst import CMD0_ECHO_CMD, P2PKIND_ACCTSHARE
from peer.TCmdStringSck import TCmdStringSck


class TCmdStringSckAcctShare(TCmdStringSck):
    def __init__(self, sHostAndPort, sAcctId, sAcctPwd, sClientInfo, bVerbosePrintCmdStr=True):
        TCmdStringSck.__init__(self, '@HubId', P2PKIND_ACCTSHARE, sHostAndPort,
                               sAcctId, sAcctPwd, 'Y', sClientInfo, bVerbosePrintCmdStr)

    def LoopAndProcessLogic(self):
        iCnt = 0
        while True:
            sLogicParam = 'LogParam'+str(iCnt)
            self.SendRequestCmd((CMD0_ECHO_CMD, 'Just4Test', "python"+str(iCnt), sLogicParam), sLogicParam)
            iCnt += 1
            if iCnt == 5:
                self.SendNotifyMsg(("LmtApi.NotifyMsg", 'Just4Test', "python"+str(iCnt), sLogicParam))
            if iCnt >= 10:
                break  # 10
            # time.sleep(0.1)

    def OnHandleReplyCallBack(self, sCmd0, sLogicParam, CmdStr, dwCmdId):
        PrintTimeMsg("TCmdStringSckAppShr.OnHandleReplyCallBack.sCmd0=%s,dwCmdId=%s,sLogicParam=%s,CmdStr=%s"
                    % (sCmd0, dwCmdId, sLogicParam, str(CmdStr)))
        return True


def TryTCmdStringSckAcctShare():
    cssa = TCmdStringSckAcctShare("127.0.0.1:8888", 'testCSTP', 'testCSTP', 'sClientDevInfo')
    cssa.StartMainThreadLoop()

# -------------------------------------
if __name__ == '__main__':
    TryTCmdStringSckAcctShare()
