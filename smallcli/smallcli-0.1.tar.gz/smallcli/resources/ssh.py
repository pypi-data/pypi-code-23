# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import abc
from six import add_metaclass, text_type


import os
import subprocess
import socket
import sys


class ssh(object):
    def __init__(self, ip, key=None, user=None):
        self._ip = ip
        self._key = key
        self._user = user
        self._children = []

    def run_cmd(self, command, _connect=False):
        cmd = self._build_ssh(command)
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            if _connect and ex.returncode == 255:
                raise RuntimeWarning(ex.output.strip())
            raise RuntimeError('ssh returned exit status %d:\n%s'
                    % (ex.returncode, ex.output.strip()))

    def fork_cmd(self, command, name=None):
        if name is None:
            name = command
        cmd = self._build_ssh(command)
        pid = os.fork()
        if (pid != 0):
            # In the parent process
            self._children.append((pid, name))
            return pid
        # In the child process: use os._exit to terminate
        try:
            # Actually ignore output on success, but capture stderr on failure
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            raise RuntimeError("Child process '%s' failed:\n"
                    'ssh returned exit status %d:\n%s'
                    % (name, ex.returncode, ex.output.strip()))
        os._exit(0)

    def scp_put(self, src, dst):
        """Copy src file from local system to dst on remote system."""
        cmd = [ 'scp',
                '-B',
                '-oStrictHostKeyChecking=no',
                '-oUserKnownHostsFile=/dev/null',
                '-oLogLevel=ERROR']
        if self._key is not None:
            cmd.extend(['-i', self._key])
        cmd.append(src)
        remote = ''
        if self._user is not None:
            remote += self._user + '@'
        remote += self._ip + ':' + dst
        cmd.append(remote)
        try:
            # Actually ignore output on success, but capture stderr on failure
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            raise RuntimeError('scp returned exit status %d:\n%s'
                    % (ex.returncode, ex.output.strip()))

    def scp_get(self, src, dst):
        """Copy src file from local system to dst on remote system."""
        cmd = [ 'scp',
                '-B',
                '-oStrictHostKeyChecking=no',
                '-oUserKnownHostsFile=/dev/null',
                '-oLogLevel=ERROR' ]
        if self._key is not None:
            cmd.extend(['-i', self._key])
        remote = ''
        if self._user is not None:
            remote += self._user + '@'
        remote += self._ip + ':' + src
        cmd.append(remote)
        cmd.append(dst)
        try:
            # Actually ignore output on success, but capture stderr on failure
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            raise RuntimeError('scp returned exit status %d:\n%s'
                    % (ex.returncode, ex.output.strip()))

    def _build_ssh(self, command):
        cmd = [ 'ssh',
                '-oBatchMode=yes',
                '-oStrictHostKeyChecking=no',
                '-oUserKnownHostsFile=/dev/null',
                '-oLogLevel=ERROR' ]
        if self._key is not None:
            cmd.extend(['-i', self._key])
        remote = ''
        if self._user is not None:
            remote += self._user + '@'
        remote += self._ip
        cmd.append(remote)
        cmd.append(command)
        return cmd
'''
if __name__ == "__main__":
    a = ssh(ip="1.1.1.1", key="/home/suresh/test_rsa", user="cloud")
    #result = a.run_cmd(command="sudo apt-get update")
    #result = a.fork_cmd(command="sudo apt-get update")
    #a.scp_put(src="/home/suresh/test_rsa", dst="/home/cloud/test_rsa")
    a.scp_get(src="/home/cloud/test_rsa", dst="/home/suresh/test1_rsa")
    #print result
'''