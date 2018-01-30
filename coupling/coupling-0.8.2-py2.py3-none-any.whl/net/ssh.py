# -*- coding: utf-8 -*-

import os
import re
import six
import time
import posixpath
import stat
import errno
import paramiko

from coupling import fs

import logging
logger = logging.getLogger(__name__)


class SSHError(Exception):
    pass


class TimeoutExpired(SSHError):
    def __init__(self, cmd, timeout):
        self.cmd = cmd
        self.timeout = timeout

    def __str__(self):
        return "<TimeoutExpired(cmd:%s, timeout:%s)>" % (self.cmd, self.timeout)


class ExecCommandResponse(object):
    def __init__(self, cmd, stdin, stdout, stderr):
        self.cmd = cmd
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self._channel = self.stdout.channel
        self.peer = self._channel.getpeername()
        self.returncode = None

    def communicate(self, input=None, timeout=None):
        # for using timeout is not None, we should set get_pty=True when exec command.
        stdout = None
        stderr = None
        if input is not None:
            raise NotImplementedError

        try:
            self.wait(timeout)
        except TimeoutExpired:
            # non thread safe when multi-thread read.
            # the size of in_buffer when doing len() and read() may not match.
            out_size = len(self._channel.in_buffer)
            if out_size:
                stdout = self.stdout.read(out_size)

            err_size = len(self._channel.in_stderr_buffer)
            if err_size:
                stderr = self.stderr.read(err_size)
        else:
            stdout = self.stdout.read()
            self.stdout.close()
            stderr = self.stderr.read()
            self.stderr.close()

        if stdout is not None and not six.PY2:
            stdout = stdout.decode()

        if stderr is not None and not six.PY2:
            stderr = stderr.decode()

        return stdout, stderr

    def wait(self, timeout=None):
        if timeout is None:
            self.returncode = self._channel.recv_exit_status()
        else:
            start_time = time.time()
            while True:
                if self._channel.exit_status_ready():
                    self.returncode = self._channel.recv_exit_status()
                    break

                if time.time() - start_time > timeout:
                    raise TimeoutExpired(self.cmd, timeout)
                time.sleep(0.1)
        return self.returncode

    def poll(self):
        if self._channel.exit_status_ready():
            self.returncode = self._channel.recv_exit_status()
        return self.returncode


class SSHClient(paramiko.SSHClient):
    def open_sftp(self):
        return SFTPClient.from_transport(self._transport)

    def run(self, cmd, cwd=None, **kwargs):
        if cwd is not None:
            cmd = "cd %s && %s" % (cwd, cmd)
        stdin, stdout, stderr = self.exec_command(cmd, **kwargs)
        resp = ExecCommandResponse(cmd, stdin, stdout, stderr)
        return resp


class SFTPClient(paramiko.SFTPClient):
    def find(self, path, bydepth=True, exclude=None, topdir=True):
        """
        @:param bydepth: Reports the name of a directory only AFTER all its entries have been reported
        @:param exclude: a string or re pattern type, use this to exclude the path you don't want to find
        @:param topdir: whether include the top dir
        """

        def walk(dir_path, _by_depth, _exclude):
            for name in self.listdir(dir_path):
                found = posixpath.join(dir_path, name)
                if _exclude and re.search(_exclude, found):
                    logger.info("walk: skip %s", found)
                else:
                    logger.debug("walk: process %s", found)
                    if not _by_depth:
                        yield found
                    if self.isdir(found):
                        for x in walk(found, _by_depth, _exclude):
                            yield x
                    if _by_depth:
                        yield found

        if self.isdir(path):
            if topdir and not bydepth:
                yield path
            for x in walk(path, bydepth, exclude):
                yield x
            if topdir and bydepth:
                yield path
        else:
            yield path

    def getdir(self, rsrc, ldst, exclude):
        fs.mkdirs(ldst)
        for name in self.listdir(rsrc):
            rsrc_name = posixpath.join(rsrc, name)
            if exclude and exclude.search(rsrc_name):
                logger.info("scp get: skip %s", rsrc_name)
                continue
            ldst_name = os.path.join(ldst, name)
            if self.isdir(rsrc_name):
                self.getdir(rsrc_name, ldst_name, exclude)
            else:
                logger.debug("scp get: %s -> %s", rsrc_name, ldst_name)
                self.get(rsrc_name, ldst_name)

    def putdir(self, lsrc, rdst, exclude):
        self.mkdirs(rdst)
        for name in os.listdir(lsrc):
            lsrc_name = os.path.join(lsrc, name)
            if exclude and exclude.search(lsrc_name):
                logger.info("scp put: skip %s", lsrc_name)
                continue
            rdst_name = posixpath.join(rdst, name)
            if os.path.isdir(lsrc_name):
                self.putdir(lsrc_name, rdst_name, exclude)
            else:
                logger.debug("scp put: %s -> %s", lsrc_name, rdst_name)
                self.put(lsrc_name, rdst_name)

    def rmtree(self, path):
        for found in self.find(path):
            if self.isdir(found):
                self.rmdir(found)
            else:
                self.remove(found)

    def scp_remove(self, path):
        if self.isdir(path):
            self.rmtree(path)
        else:
            self.remove(path)

    def scp_get(self, rsrc, ldst, exclude=None):
        logger.info("scp get: rsrc=%s, ldst=%s, exclude=%s", rsrc, ldst, exclude)

        if exclude is not None and not isinstance(exclude, re._pattern_type):
            exclude = re.compile(exclude)

        if self.isdir(rsrc):
            self.getdir(rsrc, ldst, exclude)
        else:
            name = os.path.basename(rsrc)
            if os.path.exists(ldst):
                if os.path.isdir(ldst):
                    ldst_path = posixpath.join(ldst, name)
                else:
                    ldst_path = ldst
            else:
                if ldst.endswith("\\") or ldst.endswith("/"):
                    fs.mkdirs(ldst)
                    ldst_path = posixpath.join(ldst, name)
                else:
                    fs.mkdirs(os.path.dirname(ldst))
                    ldst_path = ldst
            logger.debug("scp get: %s -> %s", rsrc, ldst_path)
            self.get(rsrc, ldst_path)

    def scp_put(self, lsrc, rdst, exclude=None):
        logger.info("scp put: lsrc=%s, rdst=%s, exclude=%s", lsrc, rdst, exclude)

        if exclude is not None and not isinstance(exclude, re._pattern_type):
            exclude = re.compile(exclude)

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
                if rdst.endswith("\\") or rdst.endswith("/"):
                    self.mkdirs(rdst)
                    rdst_path = posixpath.join(rdst, name)
                else:
                    self.mkdirs(os.path.dirname(rdst))
                    rdst_path = rdst
            logger.debug("scp put: %s -> %s", lsrc, rdst_path)
            self.put(lsrc, rdst_path)

    def isdir(self, path):
        try:
            return stat.S_ISDIR(self.stat(path).st_mode)
        except IOError:
            return False

    def islink(self, path):
        try:
            return stat.S_ISLNK(self.stat(path).st_mode)
        except IOError:
            return False

    def exists(self, path):
        try:
            self.stat(path)
        except IOError as ioerr:
            if ioerr.errno == errno.ENOENT:
                return False
            raise
        else:
            return True

    def mkdirs(self, path, mode=0o777):
        if self.exists(path):
            if self.isdir(path):
                logger.debug("mkdirs: exists '%s', type is dir, skip", path)
            else:
                raise SSHError("mkdirs failed, path '%s' already exists, type is not dir" % path)
            return
        else:
            logger.debug("mkdirs: non-exists '%s' ", path)
            head, tail = os.path.split(path)
            if not tail:  # no tail when xxx/newdir
                head, tail = os.path.split(head)
            if head and tail:
                self.mkdirs(head, mode)
                if tail != os.path.curdir:  # xxx/newdir/. exists if xxx/newdir exists
                    logger.info("mkdirs: path=%s, mode=%s", path, mode)
                    self.mkdir(path, mode)
