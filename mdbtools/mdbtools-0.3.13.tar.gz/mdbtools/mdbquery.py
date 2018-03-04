#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbquery: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_03_06
'''

# }}}

import sys
import os
import pprint
from bson import SON
from MDButils import *
from MDBtool import MDBtool
from tictoc import TicToc

SEC_scale = 1000
MIN_scale = 1000*60
HOUR_scale = 1000*60*60
Headers  = ['Index', 'Retrieved', 'Matched', 'Total', 'Fraction', 'Time', 'Hint' ]

def scaleCount(value):
    if value >= .9*1e9:
        value = '%4.2f billion' % (value / 1e9)
    elif value >= .9*1e6:
        value = '%4.2f million' % (value / 1e6)
    elif value >= .9*1e5:
        value = '%4.2f thousand' % (value / 1e3)

    return value

def parse_keyvals(keyvals, hinted_index_as_integer):
    # This routine translates:
    #   key=value_str[,key=value_str] from CLI into dict of Mongo query syntax
    #   any index hint provided at CLI from integer into field name
    # Multiple values can be given for a key by separating with |
    # Each key represents the name of a field within the DB record

    if not keyvals:
        return []

    query_terms = []
    keynum = 0
    hinted_index_name = None

    for keyval in keyvals.split(','):
        key, _ ,value = keyval.partition('=')
        values_for_this_key = value.strip().split('|')

        if hinted_index_as_integer and (hinted_index_as_integer == keynum):
            hinted_index_name = key

        if len(values_for_this_key) > 1:
            # Be tolerant of messy input, e.g. whitespace around values
            values_for_this_key = [ k.strip() for k in values_for_this_key]
            value = {'$in' : values_for_this_key }
        query_terms.append({ key.strip() : value })
        keynum += 1

    # Multple query terms are AND-ed together
    if len(query_terms) > 1:
        query_terms = [{ '$and' : query_terms }]

    return query_terms[0], hinted_index_name
    
def emitStats(collection, query, values, pretty=False):

    found = values['nFound']
    matched = values['nMatched']
    total = values['numTotal']
    percent = 100.0 * matched / total
    matched = scaleCount(matched)
    total = scaleCount(total)

    if pretty:
        print '%-24s%-12s%-18s%-16s%7.2f%%%+11s%+9s' % (values['index'],
                    found, matched, total, percent, values['time'], values['hint'])
    else:
        print '%s\t%s\t%s\t%s\t%s\t%s\t%s' % ( values['index'],
                    found, matched, total, percent, values['time'], values['hint'])

class mdbquery(MDBtool):

    def __init__(self):
        super(mdbquery, self).__init__(version='0.2.0')

        cli = self.cli
        cli.description = 'Perform and analyze queries of MongoDB databases, '+\
                          'using simple syntax.\n\n'

        # Optional arguments
        cli.add_argument('-e', '--explain', default=True, action='store_false',
                    help='TOGGLE OFF calls to cursor.explain(); when used with '+
                         'other options like --retrieve, this can help isolate'+
                         ' the runtime of find() (lookup/match) from retrieval'+
                         ' e.g. cursor.next() or list(cursor)')
        cli.add_argument('-H', '--Hint', default=1, type=int,
                    help='integer >=1: when more than 1 key is used in query, '\
                    'this hints to Mongo which of them it should use as the '\
                    'primary search index [default: 1, or first key]')
        cli.add_argument('-i', '--iters', default=1, type=int,
                    help='iteratively perform query [default: %(default)s]')
        cli.add_argument('-l', '--list', default=False, action='store_true',
                    help='list documents as they are retrieved, implicitly '+
                         'turning on --retrieve option [default: %(default)s]')
        cli.add_argument('-n', '--numrecs', default=50, type=int,
                    help='Specify the max # documents that the query should '+\
                    'find [0 == all, default: %(default)s]')
        cli.add_argument('-r', '--retrieve', default=False, action='store_true',
                    help='after performing find() query, iteratively retrieve '+
                    'all of the docs in the result set [default: %(default)s]')
        cli.add_argument('-t', '--time', default=False, action='store_true',
                    help='include more timing info in output [default: %(default)s]')
        cli.add_argument('-w', '--what', default='all',
                    help='what info to obtain: '+
                    'all, global, collections [default: %(default)s]')
        cli.add_argument('-u', '--unique', default=False, dest='unique',
                    action='store_true',
                   help='find all unique (distinct) values for given key')

        # Positional (required) arguments
        cli.add_argument('queries', nargs='+',
                    help='One or more query expressions, each of the form\n'\
                    '   Collection_Name:Key1=value1[|value2...][,Key2=....] '\
                    'Key names equate to field names within the collection.\n'\
                    'Multiple values may be specified, delimited by |')

    def normalize(self, results):

        if self.options.verbose:
            print '\n\nexecutionStats explain results:'
            pprint.pprint(results)

        #['executionTimeMillis', 'nReturned', 'totalDocsExamined', 'executionStages', 'hint'])
        normed = {}

        # Index used in query, if any
        value  = results['queryPlanner']['winningPlan'].get('inputStage', None)
        if value:
            value = value.get('inputStage', value)
            normed['index'] = value.get('indexName','none')
        else:
            normed['index'] = 'none'

        # Execution time
        results = results['executionStats']
        value = results['executionTimeMillis']
        if value >= .9*HOUR_scale:
            value = '%2.2f hours' % (1.0 * value / HOURS_scale)
        elif value >= .9*MIN_scale:
            value = '%2.2f mins' % (1.0 * value / MIN_scale)
        elif value >= .9*SEC_scale:
            value = '%2.2f sec' % (1.0 * value / SEC_scale)
        else:
            value = str(value) + ' msec'
        normed['time'] = value

        # Number of docs inspected (in database) and returned (in results set)
        normed['nExamined'] = results['totalDocsExamined']
        normed['nFound'] = results['nReturned']

        return normed

    def do_query(self, collection, query_specification):

        opts = self.options
        collection = self.db[collection]
        n = opts.numrecs

        query, hint = parse_keyvals( query_specification, opts.Hint)

        # This can be cut/pasted right into mongo shell db.<collection>
        print '\nQUERY: db.' + collection.name + '.find(' + str(query) +')'
        print 'RESULTS:'

        if not opts.unique:
            if opts.pretty:
                print '%-24s%-12s%-18s%-16s%-11s%-11s%-7s' % \
                    (Headers[0], Headers[1], Headers[2], \
                    Headers[3], Headers[4], Headers[5], Headers[6])
            else:
                print '\t'.join(Headers)


        if opts.time:
            t = TicToc(incremental=True)

        # Perform query
        if opts.unique:
            key = query.keys()[0]
            results = collection.distinct(key)
            print '%d distinct results found for key %s:' % (len(results), key)
            pprint.pprint(results)
            return

        if hint:
            if opts.verbose:
                print '\tHINTED: ' + str(hint)
            cursor = collection.find(query)
            cursor.hint( [(hint, 1)] )              # 1 = pymongo.ASCENDING
            cursor.limit(n)
        else:
            cursor = collection.find(query, limit=n)

        if opts.time:
            t.toc('initial find() command')

        if opts.explain:
            results = cursor.explain()
            if opts.verbose:
                print 'FULL explain results:'
                pprint.pprint(results)

            results = self.normalize( results )
            # Splice in extra fields: total num records/objs in collection, and hint
            results['nMatched'] = cursor.count()
            results['numTotal'] = collection.count()
            results['hint'] = hint
            emitStats(collection, str(query), results, opts.pretty)

        if opts.time:
            t.toc('explain() command and emitStats() function')

        if opts.retrieve:
            results = list(cursor)
            if opts.time:
                t.toc('retrieve %s documents, via list(cursor)' % len(results))
            if opts.list:
                print '\tRECORDS are: '
                pprint.pprint(results, indent=4)
                if opts.time:
                    t.toc('listing %s documents' % len(results))

    def do_queries(self):
        opts = self.options
        queries = opts.queries

        if len(queries) == 1 and os.path.isfile(queries[0]):
            queries = open(queries[0], 'rb').read().split('\n')

        # Multiple queries can be specified at CLI or in file
        for q in queries:
            # Partition each Collection:key=value [,key=value ...] query into
            # two pieces: (1) collection name and (2) key/value terms
            q = q.split(':')
            if len(q) < 2:
                q.append('')

            collection = q[0]
            if self.collectionExists(collection):
                for _ in range(opts.iters):
                    self.do_query(collection, q[1])
            else:
                eprint('Skipping query on non-existing collection: '+collection)
                continue

    def execute(self):
        super(mdbquery, self).execute()
        self.options.pretty = sys.stdout.isatty()
        if self.options.list:
            self.options.retrieve = True

        # User supplies an index hint in the natural, ones-based way, but
        # for convenience this tool internally uses it as zero-based
        if self.options.Hint > 0:
            self.options.Hint = self.options.Hint-1
        else:
            self.options.Hint = 0

        self.do_queries()

if __name__ == '__main__':
    tool = mdbquery()
    tool.execute()
