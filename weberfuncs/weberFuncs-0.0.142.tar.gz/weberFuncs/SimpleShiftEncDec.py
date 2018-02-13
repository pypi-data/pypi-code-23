#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""
    2016/8/11  WeiYanfeng
    简单串加密、解密函数
    目的是为对一些敏感信息进行一下简单防护。

    WeiYF.20170605 该单元在 Python 3 下不能正常工作；需要时再进行具体处理。
    WeiYF.20180213 支持 Python 3 。

"""
from .python_version import IsPython3OrLater

import base64


def SimpleShiftEncode(sKey, sSrc):
    if sKey == '':
        sKey = ' '  # 若是空串，改为空格
    if IsPython3OrLater():
        byKey = sKey.encode('utf8')
        bySrc = sSrc.encode('utf8')
        # print(bySrc)
        lsEnc = []
        for i in range(len(bySrc)):
            cKey = byKey[i % len(byKey)]
            cEnc = (bySrc[i] + cKey) % 256
            lsEnc.append(cEnc)
        return base64.urlsafe_b64encode(bytes(lsEnc))
    lsEnc = []
    for i in range(len(sSrc)):
        cKey = sKey[i % len(sKey)]
        cEnc = chr((ord(sSrc[i]) + ord(cKey)) % 256)
        lsEnc.append(cEnc)
    return base64.urlsafe_b64encode("".join(lsEnc))
    # return base64.urlsafe_b64encode(lsEnc)


def SimpleShiftDecode(sKey, sEnc):
    if sKey == '':
        sKey = ' '  # 若是空串，改为空格
    if IsPython3OrLater():
        byKey = sKey.encode('utf8')
        if type(sEnc) == bytes:
            byEnc = sEnc
        else:
            byEnc = sEnc.encode('utf8')
        # print(byEnc)
        lsDec = []
        byEnc = base64.urlsafe_b64decode(byEnc)
        for i in range(len(byEnc)):
            cKey = byKey[i % len(byKey)]
            cDec = (256 + byEnc[i] - cKey) % 256
            lsDec.append(cDec)
        byDec = bytes(lsDec)
        # print(byDec)
        return byDec.decode('utf8')
    lsDec = []
    sEnc = base64.urlsafe_b64decode(sEnc)
    for i in range(len(sEnc)):
        cKey = sKey[i % len(sKey)]
        cDec = chr((256 + ord(sEnc[i]) - ord(cKey)) % 256)
        lsDec.append(cDec)
    return "".join(lsDec)


def mainEncDec():
    sKey = 'key'
    sV = 'Hello测试test撒大as'
    # sV = ''
    sEnc = SimpleShiftEncode(sKey, sV)
    print(sEnc)
    sDec = SimpleShiftDecode(sKey, sEnc)
    print(sDec)


if __name__ == "__main__":
    mainEncDec()