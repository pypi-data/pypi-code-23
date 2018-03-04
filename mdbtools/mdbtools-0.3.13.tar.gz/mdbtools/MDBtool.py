#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

MDBtool.py: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016-11-23
'''

# }}}

from __future__ import print_function
import sys
import os
import traceback
from pymongo import MongoClient, version as pyMongoClientVersion, IndexModel
from MDBnetrc import MDBnetrc
from MDBcli import MDBcli
from MDButils import *

class MDBtool(object):
    ''' Base class for each tool '''

    def __init__(self, version=None):

        self.cli = MDBcli(version=version)
        # Derived classes can/should add custom options/description/version &
        # behavior in their respective __init__()/execute() implementations

    def connect(self, dbname, host, port=27017):

        opts = self.options
        endpoint = "%s:%s/%s" % (host, port, dbname)
        if opts.verbose:
            print("Connecting to " + endpoint)

        try:
            # Connect to database, authenticating if necessary
            user, _, password = MDBnetrc().authenticators(host)
            connection = MongoClient(host, port)
            db = connection[dbname]

            # Easter egg for Broadies: no auth needed for certain internal VMs
            authenticate = opts.authenticate and host.lower() not in ['fbdev']
            if authenticate:
                db.authenticate(user, password)

        except Exception as e:
            eprint("Could not connect to " + endpoint)
            if opts.verbose:
                traceback.print_exc()
            sys.exit(1)

        return db, connection

    def collectionExists(self, name, database=None):
        if not database:
            database = self.db
        return (name in database.collection_names())

    def execute(self):
        self.options = self.cli.parse_args()
        op = self.options
        self.db, self.connection = self.connect(op.dbname, op.server, op.port)

    def status(self):
        # Emit system info (as header comments suitable for TSV, etc) ...
        db_server_version = self.connection.server_info()['version']
        print('#' )
        print('# %-22s = %s' % (self.__class__.__name__ + ' version ', \
                                                self.cli.version))
        print('# Server Name            = %s' % self.options.server)
        print('# Database Name          = %s' % self.options.dbname)
        print('# MongoDB server version = %s' % db_server_version)
        print('# PyMongo client version = %s' % pyMongoClientVersion)
        print('#')

if __name__ == "__main__":
    tool = MDBtool()
    tool.execute()
    tool.status()
