# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

import time
import unittest
from datetime import timedelta

from trac.db.api import DatabaseManager
from trac.test import EnvironmentStub
from trac.util.datefmt import datetime_now, to_utimestamp, utc

from tracspamfilter.filtersystem import FilterSystem
from tracspamfilter.model import LogEntry


def reset_db(env):
    DatabaseManager(env).drop_tables(
        ('spamfilter_bayes', 'spamfilter_log',
         'spamfilter_report', 'spamfilter_statistics'))
    env.reset_db()


class LogEntryTestCase(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub()
        FilterSystem(self.env).upgrade_environment()

    def tearDown(self):
        reset_db(self.env)

    def _insert_log_entries(self, num_entries):
        """Helper method to insert log entries."""
        now = to_utimestamp(datetime_now(utc))
        self.env.db_transaction.executemany("""
            INSERT INTO spamfilter_log
             (time,path,author,authenticated,ipnr,headers,content,
              rejected,karma,reasons,request)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [(now + i, '/ticket/1', 'Joe Smith <joesmith@example.com',
                   0, '::1', '', "Test", 1, -1, None, None)
                  for i in xrange(0, num_entries)])

    def test_delete_one(self):
        """Delete one entry."""
        n = 1
        self._insert_log_entries(n)

        self.assertEqual(n, len(list(LogEntry.select(self.env))))
        LogEntry.delete(self.env, n)
        self.assertEqual(0, len(list(LogEntry.select(self.env))))

    def test_delete_many(self):
        """Delete many entries."""
        n = 10
        self._insert_log_entries(n)

        self.assertEqual(n, len(list(LogEntry.select(self.env))))
        LogEntry.delete(self.env, range(1, n + 1))
        self.assertEqual(0, len(list(LogEntry.select(self.env))))

    def test_purge(self):
        now = datetime_now()
        oneweekago = time.mktime((now - timedelta(weeks=1)).timetuple())
        onedayago = time.mktime((now - timedelta(days=1)).timetuple())
        req = None

        LogEntry(self.env, oneweekago, '/foo', 'john', False, '127.0.0.1',
                 '', 'Test', False, 5, [], req).insert()
        LogEntry(self.env, onedayago, '/foo', 'anonymous', False, '127.0.0.1',
                 '', 'Test', True, -3, [], req).insert()

        LogEntry.purge(self.env, days=4)

        log = list(LogEntry.select(self.env))
        self.assertEqual(1, len(log))
        entry = log[0]
        self.assertEqual('anonymous', entry.author)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LogEntryTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
