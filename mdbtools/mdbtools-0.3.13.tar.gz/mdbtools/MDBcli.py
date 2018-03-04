#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

This file is part of mdbtools.  See the <root>/COPYRIGHT file for the
SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016-03-04
'''

# }}}

import os
import re
import sys
import argparse
from MDButils import *

# Stop Python from complaining when I/O pipes are closed
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

WHITESPACE = re.compile('[ \t\n]')
RCFILENAME = ".mdbtoolsrc"

def getDefaultConfig():

    # Look first for rc (config) file in user's $HOME directory
    rcfile = os.path.expanduser("~")
    rcfile = os.path.join(rcfile, RCFILENAME)

    config = {
        'Server'   : 'localhost',
        'Database' : 'test',
        'Port'     : '27017'
    }

    # A safer rcfile alternative is to read line by line, looking for key=value pairs
    try:
        rcfile = open(rcfile, "r")
    except Exception as e:
        rcfile = None

    if rcfile:
        for line in rcfile:
            tokens = line.strip().split("=")
            if len(tokens) != 2:
                continue
            for token in tokens:
                if WHITESPACE.search(token):
                    eprint("Skipping line: <%s>\n"\
                        "Neither key nor value may contain whitespace in %s" %
                        (line, RCFILENAME))
                    tokens = None
            if tokens:
                exec("=".join(tokens), config)

    return config['Server'], config['Database'], config['Port']

class MDBcli(argparse.ArgumentParser):
    ''' Encapsulates interactions with the command line, making it easy for
    all mdbtools to share a core set of common CLI self.args.  '''

    ALL_REMAINING_ARGS = argparse.REMAINDER

    def __init__(self, descrip=None, version=None):
    
        if not descrip:
            descrip =  'MDBtools: a suite of CLI tools to simplify interaction\n'
            descrip += 'with MongoDB, directly from the *NIX command line and\n'
            descrip += 'little to no JavaScript coding required.\n'

        if not version:
            version = MDB_VERSION

        super(MDBcli,self).__init__(description=descrip,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        (server, database, port) = getDefaultConfig()

        self.add_argument('-a', '--authenticate',default="yes",
                help='Require credentials to access DB server? [%(default)s]')
        self.add_argument('-d', '--dbname', default=database,
                    help='database to which this should connect [%(default)s]')
        self.add_argument('-p', '--port', type=int, default=port,
                help='the port at which server offers database [%(default)s]')
        self.add_argument('-s', '--server', default=server,
                help='the server hosting the database [%(default)s]')
        self.add_argument('--verbose', dest='verbose', action='count', 
                help='set verbosity level [%(default)s]')
        self.add_argument('--version',action='version',version=version)
        self.version = version

    def parse_args(self):

        args = super(MDBcli,self).parse_args()

        # Be flexible in how we allow authentication to be turned on/off
        auth = args.authenticate.lower()
        args.authenticate = (auth in ["y", "yes", '1', 'true'])

        return args

    def ok_to_continue(self, message=None):

        if message:
            mprint(message)

        mprint("If this is OK, shall I continue? (Y/N) [N]",end=' ')
        sys.stdout.flush()
        answer = sys.stdin.readline().rstrip('\n')
        mprint('')
        if answer not in ["y", "yes", "Y", "Yes", '1', 'true']:
            mprint("OK, exiting without doing anything further.")
            sys.exit(0)

if __name__ == "__main__":
    cli = MDBcli()
    options = cli.parse_args()
    mprint(str(options))
