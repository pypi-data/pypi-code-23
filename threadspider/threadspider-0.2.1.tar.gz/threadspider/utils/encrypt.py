#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2017/1/17.
# ---------------------------------


import  hashlib
def md5(str,hex=True):
    '获取字符串的md5校验'
    m=hashlib.md5()
    m.update(str)
    if hex==True:
        return m.hexdigest()
    else:
        return  m.digest()