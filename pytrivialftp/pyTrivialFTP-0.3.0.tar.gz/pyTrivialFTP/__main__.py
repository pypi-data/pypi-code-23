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


import getopt
import sys
from pyTrivialFTP import pyTrivialFTPShell


def short_usage():
    print >>sys.stderr, """Usage:
    pyTrivialFTP -H HOSTNAME -U USERNAME -P PASSWORD -w WORK_DIR [ -p PATTERN ]
Try `pyTrivialFTP --help' for more information."""


def full_usage():
    print >>sys.stderr, """Usage:
    pyTrivialFTP -H HOSTNAME -U USERNAME -P PASSWORD -w WORK_DIR [ -p PATTERN ]
The poor man's API for accessing data on a remote FTP repository.
      --help                        display this help and exit
  -H, --hostname       HOSTNAME     name of the cache
  -U, --username       USERNAME     base directory of the cache
  -P, --password       PASSWORD     apply a patter match
  -w, --wd             WORK_DIR     apply a patter match
  -p, --pattern        PATTERN      apply a patter match"""


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hH:U:P:w:p:",
                                   ["help", "hostname=", "username=", "password=", "wd=", "pattern=", ])
    except getopt.GetoptError, err:
        print >>sys.stderr, err
        short_usage()
        sys.exit(2)

    hostname = None
    username = None
    password = None
    wd = None
    pattern = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            full_usage()
            sys.exit()
        elif opt in ("-H", "--hostname"):
            hostname = arg
        elif opt in ("-U", "--username"):
            username = arg
        elif opt in ("-P", "--password"):
            password = arg
        elif opt in ("-w", "--wd"):
            wd = arg
        elif opt in ("-p", "--pattern"):
            pattern = arg

    # pre-flights sanity checks
    if not hostname:
        print >>sys.stderr, "Host name not specified!\n"\
            "A host name can be specified via the --hostname switch."
        sys.exit(2)
    if not username:
        print >>sys.stderr, "User name not specified!\n"\
            "A used name can be specified via the --username switch."
        sys.exit(2)
    if not password:
        print >>sys.stderr, "Password not specified!\n"\
            "A password can be specified via the --password switch."
        sys.exit(2)
    if not wd:
        print >>sys.stderr, "Working directory not specified!\n"\
            "A working directory can be specified via the --wd switch."
        sys.exit(2)

    # connect to the FTP shell
    pyTrivialFTPShell(hostname, username, password, wd, pattern, autologin=True).cmdloop()


if __name__ == "__main__":
    main()


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
