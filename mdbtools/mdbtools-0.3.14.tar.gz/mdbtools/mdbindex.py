#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbindex: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_07_25
'''

# }}}

from __future__ import print_function
from MDBtool  import *
from MDButils import *

class mdbindex(MDBtool):

    def __init__(self):
        super(mdbindex, self).__init__(version="0.2.1")

        cli = self.cli
        cli.description = 'Add one or more indexes to one or more collections '\
						  'in a MongoDB database'

        # Optional arguments
        cli.add_argument('-c', '--compound', action='store_true',
                    help='instead of creating single-key indexes (the '\
                    'default), combine all of the '\
                    'indexes specified for a given collection into a ' \
                    'single compound index')
        cli.add_argument('-f', '--foreground', action='store_true',
                    help='by default indexes will built in the background, so '\
                    'that the database and collections can continue to be '\
                    'accessed; specifying this option will TURN THAT OFF: '\
                    'the indexes will be built in the foreground, during '\
                    'which time the database will be completely locked; this '\
                    'can severely impact the performance and usability of '\
                    'your application, so DO NOT use this option unless '\
                    'you really know what you\'re doing')
        cli.add_argument('-r', '--remove', action='store_true',
                    help='instead of adding the given index(es) to the '\
                    'collection, attempt to delete them if they exist')

        # Positional (required) arguments
        cli.add_argument('indexes',nargs='+',
                    help='One or more index expressions, each of the form:\n'\
                    '       collection_name:key[=direction][,key[=direction]...]'\
                    '\nDirection can be 1 or -1 (ASCENDING/DESCENDING), '\
                    'and defaults to 1 if not specified. No white space is '\
                    'permitted within an index expression')

    def create_indexes(self, collection, index_terms):

        indexes = list()
        background = not self.options.foreground

        if self.options.compound:
            indexes.append( IndexModel( index_terms, background=background) )
            print("Adding compound index %s to collection %s " \
                                     % (str(index_terms), collection))
        else:
            for iterm in index_terms:
                indexes.append( IndexModel( [iterm], background=background) )
                print("Adding index %s_%d to collection %s " \
                                    % (iterm[0], iterm[1], collection))

        print("Indexes will be built in the ",end="")
        if background:
            print("background: database will remain accessible")
        else:
            print("foreground: database will be locked and completely inaccessible")

        self.db[collection].create_indexes(indexes)

    def remove_indexes(self, collection, index_terms):
        # Attempts to delete non-existent index/etc will be silently ignored

        try:
            if self.options.compound:
                print("Attempting to drop compound index %s from collection %s" \
                                                % (str(index_terms), collection))
                self.db[collection].drop_index(index_terms)
            else:
                for iterm in index_terms:
                    print("Attempting to drop index %s_%d from collection %s" \
                                                % (iterm[0], iterm[1], collection))
                    self.db[collection].drop_index([iterm])

        except Exception as e:
            print("Exception: "+str(e))

    def parse_index(self, keyvals):
        if not keyvals:
            return []
        index_terms = []
        for keyval in keyvals.split(','):
            key, _ , value = keyval.partition('=')
            if not value:
                value = "1"
            index_terms.append( ( key.strip(), int(value.strip()) ) )
        return index_terms

    def execute(self):
        super(mdbindex, self).execute()
        indexes = self.options.indexes

        if self.options.remove:
            index_operation = self.remove_indexes
        else:
            index_operation = self.create_indexes

        # Multiple indexes can be specified at CLI or in file
        if len(indexes) == 1 and os.path.isfile(indexes[0]):
            indexes = open(indexes[0], 'rb').read().split('\n')

        for i in indexes:
            # Partition each index spec into Collection:key[=direction][,key=[direction]...]
            i = i.split(':')
            if len(i) < 2:
                i.append('')

            collection = i[0]
            if not self.collectionExists(collection):
                eprint('Skipping non-existing collection: '+collection)
                continue

            index_operation(collection, self.parse_index( i[1] ))

if __name__ == "__main__":
    mdbindex().execute()
