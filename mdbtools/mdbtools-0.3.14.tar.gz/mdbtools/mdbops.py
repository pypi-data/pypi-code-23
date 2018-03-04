#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbops: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_07_25
'''

# }}}

#from __future__ import print_function
import sys
from MDBtool import MDBtool
import pprint

class mdbops(MDBtool):

    def __init__(self):
        super(mdbops, self).__init__(version="0.2.0")
        cli = self.cli
        desc = 'Show current operations being performed upon a given database\n'
        cli.description = desc

    def execute(self):
        super(mdbops, self).execute()
        opts = self.options
        print("Current operations on %s:%s are:" % (opts.server, opts.dbname))
        operations = self.db.current_op()["inprog"]
        if operations:
            pprint.pprint(operations)
        else:
            print("   None, zero operations are currently running")

if __name__ == "__main__":
    mdbops().execute()
