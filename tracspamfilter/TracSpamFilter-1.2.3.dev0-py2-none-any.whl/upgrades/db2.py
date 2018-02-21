# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2016 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at https://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

from trac.db import Column, DatabaseManager, Table


def do_upgrade(env, ver, cursor):
    """Add a column to the log table for storing the request headers."""
    table = [
        Table('spamfilter_log', key='id')[
            Column('id', auto_increment=True),
            Column('time', type='int'),
            Column('path'),
            Column('author'),
            Column('authenticated', type='int'),
            Column('ipnr'),
            Column('headers'),
            Column('content'),
            Column('rejected', type='int'),
            Column('karma', type='int'),
            Column('reasons')
        ]
    ]
    DatabaseManager(env).upgrade_tables(table)
