#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import hashlib

def encodePwd(plainPwd):
    """
    加密明文密码得到加密后的密码，可用于保存到配置文件中，防止明文密码泄露。
    :param plainPwd: 明文密码
    :return: 加密后的密码
    """
    md5 = hashlib.md5()
    md5.update(plainPwd)
    cypherPwd = md5.hexdigest()
    return cypherPwd