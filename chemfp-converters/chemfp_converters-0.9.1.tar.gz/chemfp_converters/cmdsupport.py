from __future__ import print_function, absolute_import

import sys
import argparse
import datetime
import os
import signal

import chemfp

from . import __version__ as chemfp_converter_version

###
# Code extracted from Python's argparse.py. Distributed under the Python license.
# Before Python 3.4, argparse --version sent the message to stderr, not stdout.
# The bug was fixed in https://bugs.python.org/issue18920 .
# chemfp supports Python 2.7 and Python 3.5+.
# This is a back-port to version 2.7

version_action = "version"
if sys.version_info.major == 2:
    class ChemfpVersionAction(argparse._VersionAction):
        def __call__(self, parser, namespace, values, option_string=None):
            version = self.version
            if version is None:
                version = parser.version
            formatter = parser._get_formatter()
            formatter.add_text(version)
            parser._print_message(formatter.format_help(), sys.stdout)
            parser.exit()

    version_action = ChemfpVersionAction

def add_version(parser):
    parser.add_argument("--version", action=version_action,
                        version="%(prog)s " + chemfp_converter_version)


###

# Want a Python2/Python3 repr() for strings which doens't show the prefix.
_string_types = (type(u""), type(b""))
def my_repr(s):
    assert isinstance(s, _string_types), s
    t = repr(s)
    if t[0] in "ub":
        return t[1:]
    return t

##

if chemfp.__version__ == "1.3":
    chemfp_supports_unicode = False
elif chemfp.__version__ [:2] >= "2.":
    chemfp_supports_unicode = True
else:
    # I think I'll be adding Unicode support for 1.4.
    # Don't want to hard-code that assumption in.
    def _check_chemfp_unicode_support():
        import io
        f = io.BytesIO(b"#FPS1\nABCD\tone\n")
        reader = chemfp.open(f)
        id, fp = next(reader)
        return isinstance(id, type(u""))

    chemfp_supports_unicode = _check_chemfp_unicode_support()

###
class VarName(object):
    def __init__(self, varname):
        self.varname = varname
    def __call__(self, value):
        for c, name in (("\n", "newline"), ("\r", "linefeed"), ("\0", "NUL")):
            if c in value:
                raise argparse.ArgumentError(
                    None, "--%s must not contain a %s character" % (self.varname, name))
        return value

_parse_type = VarName("type")
_parse_software = VarName("software")
_parse_source = VarName("source")

def _parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError as err:
        raise argparse.ArgumentError(None, "--date: " + str(err))

## '#type="

def add_type_flag(parser, extra_help=""):
    if extra_help != "":
        extra_help = " " + extra_help

    parser.add_argument(
        "--type", type=_parse_type,
        help="specify the 'type' value" + extra_help)

def add_no_type_flag(parser):
    parser.add_argument(
        "--no-type", action="store_true",
        help="do not include the type in the metadata")

def add_both_type_flags(parser, extra_help=""):
    g = parser.add_mutually_exclusive_group()
    add_type_flag(g, extra_help)
    add_no_type_flag(g)

## '#software='

def add_software_flag(parser):
    parser.add_argument("--software", type=_parse_software,
                        help="specify the 'software' metadata value")

## '#source='

def add_source_flag(parser, extra=""):
    if extra != "":
        extra = " " + extra
    parser.add_argument(
        "--source", type=_parse_source, action="append",
        help="specify the 'source' metadata value. May be specified multiple times." + extra)

## '#date='

now_time = datetime.datetime.utcnow().isoformat().split(".")[0]

def add_date_flag(parser, extra_help=""):
    # Handle 'date'/'--no-date'
    if extra_help != "":
        extra_help = " " + extra_help

    parser.add_argument(
        "--date", type=_parse_date,
        help="specify the 'date' metadata value" + extra_help +
             ". This must be in ISO format (eg, %r) and should be in UTC." % (now_time,))

def add_no_date_flag(parser):
    parser.add_argument(
        "--no-date", action="store_true",
        help="do not include the source in the metadata")

def add_both_date_flags(parser, extra_help=""):
    g = parser.add_mutually_exclusive_group()
    add_date_flag(g, extra_help)
    add_no_date_flag(g)

#
def add_output(parser):
    parser.add_argument(
        "--output", "-o", metavar="FILENAME",
        help="save the fingerprints to FILENAME (default=stdout)")
    parser.add_argument(
        "--out", metavar="FORMAT", dest="output_format", choices=("fps", "fps.gz", "fpb"),
        help="output fingerprint format. One of fps, fps.gz, or fpb. (default guesses from output filename, or is 'fps')")

#####

def get_output_metadata(metadata, args):
    m = metadata.copy()

    if getattr(args, "no_type", False):
        m.type = None
    elif getattr(args, "type", None) is not None:
        m.type = args.type

    if getattr(args, "no_software", False):
        m.software = None
    elif getattr(args, "software", None) is not None:
        m.software = args.software
    
    if getattr(args, "no_source", False):
        m.sources = []
    elif getattr(args, "source", None):
        m.sources = args.source # will be a list

    if getattr(args, "no_date", False):
        m.date = None
    elif getattr(args, "date", None) is not None:
        # chemfp 1.3 requires a string. chemfp 3.1 accepts a datetime
        m.date = args.date.isoformat().split(".", 1)[0]
    else:
        # If given a datetime, convert to a string for chemfp 1.3
        if hasattr(m.date, "isoformat"):
            m.date = m.date.isoformat().split(".", 1)[0]

    return m

#####

def die(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.stderr.flush()
    raise SystemExit(1)

#####

def get_file_creation_date(filename):
    try:
        ctime = os.stat(filename).st_ctime
    except IOError:
        return None
    return datetime.datetime.utcfromtimestamp(ctime)

#####
def run(main_func):
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow ^C to kill the process.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL) # Allow the output pipe to be closed
    try:
        main_func()
    except KeyboardInterrupt:
        raise SystemExit(2)
