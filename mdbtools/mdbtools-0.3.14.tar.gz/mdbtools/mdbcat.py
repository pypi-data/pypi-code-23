#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbcat: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_05_08
'''

# }}}

import sys
import os
import pprint
from MDButils import *
from MDBtool import MDBtool

__MISSING_VALUE__ = ""

class mdbcat(MDBtool):

    @staticmethod
    def __quote_csv(record):
        record = str(record)
        if ',' in record:
            record = '"%s"' % record
        return record

    def __init__(self):
        super(mdbcat, self).__init__(version="0.2.0")

        self.delimiter    = None
        self.formatter    = None
        self.writer       = self.jsonOutput
        self.headers = None

        cli = self.cli
        cli.description = 'Display the contents of one or more collections, '+\
            'in concatenated form, optionally saving to a new collection.'

        # Optional arguments
        cli.add_argument('-c', '--chunkSize', type=int, default=500,
                help='specify the number of documents to retrieve per '+\
                'iteration of the read loop [default: %(default)s]')
        #cli.add_argument('-e', '--extend', help='extend an existing '+\
        #        'named collection by appending the results from here')
        cli.add_argument('-f', '--format', default='json', type=str,
                help='default this tool outputs JSON; tables may be '+\
                     'output by specifying format values of tsv or csv, '+\
                     '(respectively for tab- or comma-separated values)')
        #cli.add_argument('-o', '--output', help='save the results to a '+\
        #        'new collection with the given name')
        cli.add_argument('-l', '--limit', default=None, type=int,
                help='display only LIMIT # of records, instead of all]')

        # Positional (required) arguments
        cli.add_argument('collections', nargs=cli.ALL_REMAINING_ARGS,
                                help='one or more collection names\n\n')

    def validate(self):
        # Warn and then ignore non-existent collection names
        opts = self.options
        validCollections = []
        for collection in opts.collections:
            if self.collectionExists(collection):
                validCollections.append(collection)
            else:
                eprint("No such collection: "+collection)
                continue
        opts.collections = validCollections

        # Determine how to write output
        opts.format = opts.format.lower()
        if opts.format == 'csv':
            self.delimiter = ','
            self.formatter = self.__quote_csv
            self.writer = self.tableOutput
        elif opts.format == 'tsv':
            self.delimiter = '\t'
            self.formatter = eval('str')
            self.writer = self.tableOutput
        else:
            opts.format = 'json'            # forcibly ignore any junk input

        # Remainder of this code is for when --extend/--output are enabled
        # Destination collection already exists: oh my, what to do?
        #if opts.force:
        #    self.db[opts.To].drop()
        #else:
        #    eAbort("%s collection already exists in %s:%s" % \
        #                (opts.To, opts.server, opts.dbname), err=102)

    def index(self):
        # Not used yet: but when --extend/--output options are enabled
        # this will be used to replicate indexes from source collections
        index_info = From.index_information()
        index_info.pop("_id_", None)
        indexes = []
        for idx in index_info.values():
            indexes.append( IndexModel(idx["key"]) )

        # Add all indexes in one call, to iterate single time over data
        To.create_indexes(indexes)

    def tableOutput(self, documents):

        if not self.headers:
            # Inspect first document as a reasonable proxy for column headerss.
            # For that we morph the Mongo cursor into a Python list, and examine
            # the first element; this is better than using the cursor next() and
            # rewind() methods, which would send a second query to the server
            documents = list(documents)
            self.headers = documents[0].keys()
            print(self.delimiter.join(self.headers))

        for document in documents:
            cols = list()
            for column in self.headers:
                value = document.get(column, __MISSING_VALUE__)
                cols.append(self.formatter(value))
            print(self.delimiter.join(cols))

    def jsonOutput(self, documents):
        # MongoDB 3.2 Python bindings do not expose pretty(), so we use pprint
        for document in documents:
            pprint.pprint(document)

    def cat(self, collection):
        opts = self.options
        numSeen = 0
        collection = self.db[collection]
        numTotal = collection.count()
        if opts.limit:
            numTotal = min(numTotal, int(opts.limit))

        chunkSize = min(opts.chunkSize, numTotal)
        filter = None
        ignore = {'_id':0}

        while True:
            documents = collection.find(filter, ignore)
            documents.skip(numSeen).limit(chunkSize)
            if not documents or documents.count()==0:
                break
            self.writer(documents)
            numSeen += documents.count(with_limit_and_skip=True)
            if numSeen >= numTotal:
                break

    def execute(self):
        super(mdbcat, self).execute()
        self.validate()
        for collection in self.options.collections:
            self.cat(collection)

if __name__ == "__main__":
    mdbcat().execute()
