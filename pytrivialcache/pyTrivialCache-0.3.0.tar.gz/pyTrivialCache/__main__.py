# pyTrivialCache - The poor man's API for manipulating a file system cache

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

from pyTrivialCache import pyTrivialCacheShell


def short_usage():
    print >>sys.stderr, """Usage:
    pyTrivialCache -b BASEDIR [ -n NAME ] [ -p PATTERN ]
Try `pyTrivialCache --help' for more information."""


def full_usage():
    print >>sys.stderr, """Usage:
    pyTrivialCache -b BASEDIR [ -n NAME ] [ -p PATTERN ]
The poor man's API for manipulating a file system cache.
      --help                       display this help and exit
  -b, --basedir       BASEDIR      base directory of the cache
  -n, --name          NAME         name of the cache
  -p, --pattern       PATTERN      apply a pattern match"""


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hb:n:p:",
                                   ["help", "basedir=", "name=", "pattern=", ])
    except getopt.GetoptError, err:
        print >>sys.stderr, err
        short_usage()
        sys.exit(2)

    name = None
    basedir = None
    pattern = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            full_usage()
            sys.exit()
        elif opt in ("-b", "--basedir"):
            basedir = arg
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-p", "--pattern"):
            pattern = arg

    # pre-flights sanity checks
    if not basedir:
        print >>sys.stderr, "Cache basedir not specified!\n"\
            "A used-defined basedir can be specified via the --basedir switch."
        sys.exit(2)

    # connect to the cache shell
    pyTrivialCacheShell(basedir, name, pattern).cmdloop()


if __name__ == "__main__":
    main()


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
