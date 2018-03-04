#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbload: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:   Sept 26, 2016
'''

# }}}

import os
import sys
import getpass
from csv import DictReader, Sniffer
from MDBtool import MDBtool
from MDButils import *

class mdbload(MDBtool):

    DELIMITERS=',	|;:'

    def __init__(self):
        super(mdbload, self).__init__(version="0.1.0")

        cli = self.cli
        delims = list(mdbload.DELIMITERS)
        delims[1] = 'TAB'
        cli.description = 'Easy way to load tables of data into MongoDB '+\
                    'collections. Supports the\nfollowing delimiters:'+\
                    '\t' + '  '.join(delims) + '\n\n'

        # FIXME:  add l,--delimiter flag to easily support new delimiters
        cli.add_argument('-c', '--chunksize', default=5000,
                help='how many rows to read/insert at a time? [%(default)s]')
        cli.add_argument('-e', '--extend', action='store_true',
                help='extend collection if it already exists? [False]')
        cli.add_argument('-f', '--force', action='store_true',
                help='replace collection if it already exists? [False]')

        cli.add_argument('-x', '--suffix', default='', nargs='?',
                help='Append __SUFFIX to the name of the collection that '+\
                     'is created.  If this flag is used but a SUFFIX value '+\
                     'is not supplied, then the suffix will be __$LOGNAME')

        # Positional (required) arguments
        cli.add_argument('load_expressions',nargs='+',
                help='One or more file load expressions, each having the form'+\
                     '\n   collection_name:/path/to/file1[,/path/to/file2]\n' +\
                     'This argument may also point to a single file which '   +\
                     'contains one load expression per line')

    def insert(self, collection, rows):
        if rows:
            self.db[collection].insert(rows)
        else:
            print 'No rows to insert for '+collection

        sys.stdout.flush()            # helpful when tee is used for logging

    def generate_name(self, name):

        # Generate collection name by appending suffix if any provided
        suffix = self.options.suffix
        if suffix is None:
            suffix = getpass.getuser()

        # But don't add it if it's already there
        if not name.endswith(suffix):
            name += suffix

        return name

    def load_one(self, collection, filename, header_map=None, columns_to_add=None,
                                            row_modifier=None, to_lower=True):

        collection = self.generate_name(collection)

        # Guess file type by passing first 2 non-comment/blank lines to sniffer
        fp = open(filename)
        lines = []
        while len(lines) < 2:
            line = fp.readline()
            if not line:
                break                                   # file contains <2 lines
            if not line or line.lstrip()[0] == '#':
                continue
            lines.append(line)

        lines = "\n".join(lines)
        if not lines:
            eprint('Skipping load of empty file: '+filename)
            return

        fdialect = Sniffer().sniff(lines, mdbload.DELIMITERS)
        fp.seek(0)
        reader = DictReader(fp, dialect=fdialect)
        reader.fieldnames = map(lambda x: x.replace(" ", "_"), reader.fieldnames)
        reader.fieldnames = map(lambda x: x.replace(".", ":"), reader.fieldnames)
        if to_lower:
            reader.fieldnames = map(lambda x: x.lower(), reader.fieldnames)

        if header_map:
            header = reader.fieldnames
            new_header = list()
            for colname in header:
                if colname in header_map:
                    new_header.append(header_map[colname])
                else:
                    new_header.append(colname)
            reader.fieldnames = new_header

        # Read/insert the table rows, in chunksize incrments for speed
        rows = list()
        chunksize = self.options.chunksize
        nrows = 0

        for row in reader:
            if columns_to_add:                 # Not used yet
                row.update(columns_to_add)
            if row_modifier is not None:            # Not used yet
                row = row_modifer(row)
            rows.append(row)

            if len(rows) == chunksize:
                self.insert(collection, rows)
                rows = list()
                nrows += chunksize

        if rows:
            nrows += len(rows)
            self.insert(collection, rows)

        if nrows == 0:
            eprint('No rows read from %s, collection not created' % filename)

    def load_all(self):

        lexprs = self.options.load_expressions
        if len(lexprs) == 1 and os.path.isfile(lexprs[0]):
            lexprs = open(lexprs[0], 'rb').read().split('\n')

        # Multiple lexprs can be specified at CLI or in file
        for l in lexprs:

            # Partition collection_name:/path/to/file1[,/path/to/file2 ...]
            l = l.split(':')
            if len(l) < 2:
                eprint('Skipping malformed expression, missing collection/file')
                continue

            collection = l[0]
            if self.collectionExists(collection):
                if self.options.force:
                    self.db.drop_collection(collection)
                elif not self.options.extend:
                    eprint('Skipping load to existing collection: '+collection)
                    continue

            for file in l[1].split(','):
                self.load_one(collection, file)

    def execute(self):
        super(mdbload, self).execute()
        self.load_all()

if __name__ == "__main__":
    tool = mdbload()
    tool.execute()
