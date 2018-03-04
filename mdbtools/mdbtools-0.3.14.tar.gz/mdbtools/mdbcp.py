#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbcp: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_11_23
'''

# }}}

from MDBtool  import *
from MDButils import *

class dict2obj(object):
    # Enables cleaner referencing of dict keys/values (as obj fields/attributes)
    def __init__(self, adict):
        self.__dict__.update(adict)

class mdbcp(MDBtool):

    def __init__(self):
        super(mdbcp, self).__init__(version='0.2.0')

        cli = self.cli
        cli.description = '''
        Simple CLI tool to clone a MongoDB collection.  Each collection
        may be specified as host:port/database/collection, but only the
        collection name is required in each.  Some examples are:

            mdbcp   foo    bar
            Clone resides in same database

            mdbcp   foo    otherDB/bar
            Clone to another database on the same host

            mdbcpy  foo    asgard:3000/otherDB/bar
            Clone to database on a foreign host, at a non-standard port'''

        cli.add_argument('-c', '--chunkSize', type=int, default=5000,
                    help='number of documents to copy/insert at a time')
        cli.add_argument('-f', '--force', action='store_true',
                    help='force copy: remove To collection first, if it exists')
        cli.add_argument('-n', '--numToCopy', default=None,
                    help='how many documents to copy (default: all)')

        # Positional (required) arguments
        cli.add_argument('From', help='name of existing collection')
        cli.add_argument('To', help='name of new collection to create\n')

    def parse_collection_spec(self, cspec):
        cspec = cspec.split('/')
        # Collection name is always last: see help docs for syntax
        collname = cspec[-1]
        host = port = dbname = None
        if len(cspec) == 2:
            dbname = cspec[0]
        elif len(cspec) == 3:
            dbname = cspec[1]
            server = cspec[0].split(':')
            host = server[0]
            if len(server) == 2:
                port = server[1]
        if not host:
            host = self.options.server
        if not port:
            port = self.options.port
        if not dbname:
            dbname = self.options.dbname

        return dict2obj({
                'host':host,
                'port':port,
                'dbname':dbname,
                'collname':collname,
                'db': None
                })

    def validate(self):
        opts = self.options

        # First parse the From/To specifications from CLI, and morph into dicts
        opts.From = From = self.parse_collection_spec(opts.From)
        From.db, _ = self.connect(From.dbname, From.host, From.port)

        if not self.collectionExists(From.collname, From.db):
            eprint('Collection %s does not exist in %s/%s' %
                        (From.collname, From.host, From.dbname), abort=101)

        opts.To = To = self.parse_collection_spec(opts.To)
        To.db, _ = self.connect(To.dbname, To.host, To.port)

        # Support UNIX shorthand for "copy to same name as original"
        if To.collname == ".":
            To.collname = From.collname

        # Does like-named collection already exist in destination DB?
        if self.collectionExists(To.collname, To.db):
            # Yes: oh my, what to do?
            if opts.force:
                To.db[To.collname].drop()
            else:
                eprint('%s collection already exists in %s/%s' % \
                        (To.collname, To.host, To.dbname), abort=102)

        # Things seem fine at this point, so give user feedback
        src = "%s:%s/%s/%s" % (From.host, From.port, From.dbname, From.collname)
        dest = "%s:%s/%s/%s" % (To.host, To.port, To.dbname, To.collname)
        mprint('Copying %s to %s' % (src, dest))

    def clone(self):
        # Finally ready to do the work: identify & obtain From,To collections
        opts = self.options
        From = opts.From.db[opts.From.collname]
        To   = opts.To.db[opts.To.collname]

        numCopied = 0
        totalNumRows = From.find().count()
        if opts.numToCopy:
            totalNumRows = min(totalNumRows, int(opts.numToCopy))
        chunkSize = min(opts.chunkSize, totalNumRows)

        while True:
            documents = From.find().skip(numCopied).limit(chunkSize)
            if not documents or documents.count()==0:
                break
            count = documents.count(with_limit_and_skip=True)
            To.insert(documents)
            numCopied = numCopied + count
            percentage = 100.0 * numCopied / totalNumRows
            mprint('Copied %d (of %d total, %f %%)' % \
                                (numCopied, totalNumRows, percentage))
            if numCopied >= totalNumRows:
                break
            chunkSize = min(chunkSize, totalNumRows - numCopied)

        mprint('Done copying documents ... ',end='')
        index_info = From.index_information()
        index_info.pop('_id_', None)

        indexes = []
        for idx in index_info.values():
            indexes.append( IndexModel(idx['key']) )

        # Add all indexes in one call, to iterate single time over data
        if indexes:
            mprint('now adding indexes',end='')
            To.create_indexes(indexes)
        mprint('')

    def execute(self):
        self.options = self.cli.parse_args()
        self.validate()
        self.clone()

if __name__ == '__main__':
    mdbcp().execute()
