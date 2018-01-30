# -*- coding: utf-8 -*-

import os
import re
import posixpath

import ftplib

import logging
logger = logging.getLogger(__name__)


class FTPClient(ftplib.FTP):
    def putdir(self, lsrc, rdst, exclude):
        self.mkdirs(rdst)
        for _name in os.listdir(lsrc):
            lsrc_name = os.path.join(lsrc, _name)
            if exclude and re.search(exclude, lsrc_name):
                logger.info("ftp put: skip %s", lsrc_name)
                continue
            rdst_name = posixpath.join(rdst, _name)
            if os.path.isdir(lsrc_name):
                self.putdir(lsrc_name, rdst_name, exclude)
            else:
                logger.debug("ftp put: %s -> %s", lsrc_name, rdst_name)
                self.cwd(rdst)
                file_obj = open(lsrc_name, "rb")
                self.storbinary("STOR %s" % _name, file_obj)
                file_obj.close()

    def put(self, lsrc, rdst, exclude=None):
        logger.info("ftp put: lsrc=%s, rdst=%s, exclude=%s", lsrc, rdst, exclude)
        if os.path.isdir(lsrc):
            self.putdir(lsrc, rdst, exclude)
        else:
            name = os.path.basename(lsrc)
            if self.exists(rdst):
                if self.isdir(rdst):
                    rdst_path = posixpath.join(rdst, name)
                else:
                    rdst_path = rdst
            else:
                if rdst.endswith("/"):
                    self.mkdirs(rdst)
                    rdst_path = posixpath.join(rdst, name)
                else:
                    self.mkdirs(os.path.dirname(rdst))
                    rdst_path = rdst
            logger.debug("ftp put: %s -> %s", lsrc, rdst_path)
            
            head, tail = posixpath.split(rdst_path)
            self.cwd(head)
            with open(lsrc, "rb") as f:
                self.storbinary("STOR %s" % tail, f)

    def get(self, rsrc, ldst, exclude=None):
        logger.debug("ftp get: rsrc=%s, ldst=%s, exclude=%s", rsrc, ldst, exclude)
        if self.isdir(rsrc):
            raise NotImplementedError
        else:
            with open(ldst, 'wb') as f:
                self.retrbinary("RETR " + rsrc, f.write)

    def mkdirs(self, path):
        if self.exists(path):
            if self.isdir(path):
                logger.debug("ftp mkdirs: exists '%s', type is dir, skip", path)
            else:
                raise Exception("ftp mkdirs failed, path '%s' already exists, type is not dir" % path)
        else:
            logger.debug("ftp mkdirs: non-exists '%s' ", path)
            head = os.path.split(path)[0]
            if self.exists(head):
                self.mkd(path)
            else:
                self.mkdirs(head)
                self.mkd(path)

    def exists(self, path):
        try:
            self.sendcmd("STAT %s" % path)
            return True
        except ftplib.Error:
            return False
    
    def isdir(self, path):
        try:
            self.cwd(path)
            return True
        except ftplib.Error:
            return False
