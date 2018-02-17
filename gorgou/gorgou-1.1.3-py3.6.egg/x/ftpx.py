#!/usr/bin/env python
# -*- coding: utf8 -*-

from ftplib import FTP


# 从ftp下载文件
def downloadfile(host, username, password, remotepath, localpath):
    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()
    ftp.quit()


# 从本地上传文件到ftp
def uploadfile(host, username, password, remotepath, localpath):
    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()
    ftp.quit()
