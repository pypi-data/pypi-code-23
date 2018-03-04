#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbls: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_03_06
'''

# }}}

#from __future__ import print_function
import sys
from MDBtool import MDBtool

class mdbls(MDBtool):

    def __init__(self):
        super(mdbls, self).__init__(version="0.2.0")
        # FIXME: this could also be used to list DBs on a server
        self.cli.description = 'List collections in given database\n'

    def execute(self):
        super(mdbls, self).execute()
        names = self.db.collection_names()
        opts = self.options
        if names:
            print('\n'.join( sorted(names, key=lambda n: n.lower())))

if __name__ == "__main__":
    mdbls().execute()
