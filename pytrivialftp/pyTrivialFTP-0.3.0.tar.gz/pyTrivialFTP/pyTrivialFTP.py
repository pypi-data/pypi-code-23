# pyTrivialFTP
# The poor man's API for accessing data on a remote FTP repository

# The MIT License (MIT)
#
# Copyright (c) 2014-8 Roberto Reale
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import re
import os
import cmd
from ftplib import FTP, error_perm


class pyTrivialFTP(object, FTP):

    def _log(self, priority, msg):
        # priority is ignored
        print msg

    def login(self):
        if not self.connected:
            FTP.login(self, self.username, self.password)
            self.connected = True
            self.log(20, "Connected to %s." % self.hostname)
            self.cwd(self.wd)
            self.log(20, "Changed working directory to %s." % self.wd)
        else:
            self.log(10, "Already connected.")

    def close(self):
        # logout from the remote site
        if self.connected:
            FTP.close(self)
            self.connected = False
            self.log(20, "Disconnected from %s." % self.hostname)
        else:
            self.log(10, "Already disconnected from %s." % self.hostname)

    def list(self):
        try:
            files = self.nlst()
            self.log(20, "Retrieved file list.")
        except error_perm, resp:
            if str(resp) == "550 No files found":
                self.log(10, "File list is empty.")
                return None
            else:
                raise
        return filter(self.pattern_compiled.match, files)

    def copy(self, filename, target, callback=None, binary=False):
        with open(target, 'w') as target_handler:
            def write_with_linesep(s):
                target_handler.write("%s\n" % s)
            self.log(20, "Start retrieval of remote file %s." % filename)
            if not callback:
                callback = write_with_linesep
            if binary:
                self.retrbinary("RETR " + filename, callback)
            else:
                self.retrlines("RETR " + filename, callback)
            self.log(20, "Retrieved file %s." % filename)
            target_handler.close()

    def __init__(self, hostname, username, password, wd, pattern=None, log=None, autologin=False):
        # read options
	self.hostname = hostname
	self.username = username
	self.password = password
	self.wd = wd
        if not pattern:
            self.pattern = ".*"
        else:
            self.pattern = pattern
        if not log:
            self.log = self._log
        else:
            self.log = log
        # set defaults
        self.connected = False
        self.pattern_compiled = re.compile(self.pattern)
        # initialize FTP connector
        FTP.__init__(self, self.hostname)
        # login to the remote site
        if autologin:
            self.login()

    def __del__(self):
        pass


class pyTrivialFTPShell(cmd.Cmd, pyTrivialFTP):
    intro = 'Welcome to the pyTrivialFTP shell.  Type help or ? to list commands.\n'
    prompt = '(pyTrivialFTP) '

    def do_login(self, arg):
        'Login to the remote site'
        self.login()
    def do_close(self, arg):
        'Logout from the remote site'
        self.close()
    def do_list(self, filename):
        'List contents of the remote working directory'
        for file in self.list():
            print file
    def do_copy(self, filename):
        'Copy a file onto the local working directory: COPY FILENAME'
        target = os.path.join(os.getcwd(), os.path.basename(filename))
        self.copy(filename, target)
    def do_quit(self, arg):
        'Exit'
        self.close()
        return True

    def __init__(self, hostname, username, password, wd, pattern=None, log=None, autologin=False):
	cmd.Cmd.__init__(self)
        pyTrivialFTP.__init__(self, hostname, username, password, wd, pattern, log, autologin)

    def __del__(self):
        pass


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
