# -*- coding: utf-8 -*-

import os
import subprocess


import logging
logger = logging.getLogger(__name__)


current_dir = os.path.dirname(__file__)
exe = os.path.join(current_dir, "psexec.exe")
if not os.path.exists(exe):
    exe = "psexec.exe"


class PsExec(object):
    def __init__(self, host, username, password):
        self._host = host
        self._username = username
        self._password = password

    def run(self, cmd, cwd=None, copy=False, interactive=True, timeout=10):
        command = r"%s \\%s -s -u %s -p %s" % (exe, self._host, self._username, self._password)
        if copy:
            command += " -c -f"
        if cwd:
            command += " -w %s" % cwd
        if not interactive:
            command += " -d"
        command += " -n %s %s" % (timeout, cmd)
        logger.debug("psexec command: %s", command)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        return process
