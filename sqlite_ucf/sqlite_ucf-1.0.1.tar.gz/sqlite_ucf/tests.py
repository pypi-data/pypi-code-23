# -*- coding: utf-8 -*-

import sys
import unittest

import sqlite_ucf


def unicode_chunks():
    start = 0
    for end in range(0x10, 0xd800, 0x10):
        seq = [chr(i) for i in range(start, end)]
        yield ''.join(seq)
        start = end
    seq = [chr(i) for i in range(start, 0xd800)]
    yield ''.join(seq)

    # Since RFC 3629 (November 2003), the high and low surrogate halves used by UTF-16 (U+D800 through U+DFFF) and
    # code points not encodable by UTF-16 (those after U+10FFFF) are not legal Unicode values, and their UTF-8
    # encoding must be treated as an invalid byte sequence.
    start = 0xe000
    for end in range(0xe010, sys.maxunicode, 0x10):
        seq = [chr(i) for i in range(start, end)]
        yield ''.join(seq)
        start = end


class TestSqliteUnicode(unittest.TestCase):
    def _create_db(self, data, unicode_case_folding=True):
        conn = sqlite_ucf.connect(':memory:', unicode_case_folding=unicode_case_folding)
        cur = conn.cursor()
        cur.execute('CREATE TABLE test (a text COLLATE NOCASE)')
        cur.executemany('INSERT INTO test VALUES (?)', [(x,) for x in data])
        return cur

    def _simple_db(self, unicode_case_folding=True):
        data = ['A',
                'a',
                'Á',
                'á']
        return self._create_db(data, unicode_case_folding=unicode_case_folding)

    def _simple_db2(self):
        data = ['ABC',
                'abc',
                'ÁBC',
                'ábc']
        return self._create_db(data)

    def _check_result(self, cur, expect):
        results = cur.fetchall()
        results = set(row[0] for row in results)
        self.assertEqual(results, expect)

    def test_lower_supports_unicode(self):
        cur = self._simple_db()
        # act
        cur.execute('SELECT LOWER(a) FROM test')

        self._check_result(cur, {'a', 'á'})

    def test_upper_supports_unicode(self):
        cur = self._simple_db()
        # act
        cur.execute('SELECT UPPER(a) FROM test')

        self._check_result(cur, {'A', 'Á'})

    def test_collation_supports_unicode(self):
        cur = self._simple_db()
        # act
        cur.execute('SELECT DISTINCT a FROM test')

        self._check_result(cur, {'A', 'Á'})

    def test_select_supports_unicode(self):
        cur = self._simple_db()
        # act
        cur.execute('SELECT * FROM test WHERE a = ?', ('Á',))

        self._check_result(cur, {'á', 'Á'})

    def test_select_supports_unicode2(self):
        cur = self._simple_db()
        # act
        cur.execute("SELECT * FROM test WHERE a = 'á'")

        self._check_result(cur, {'á', 'Á'})

    def test_like_supports_unicode(self):
        cur = self._simple_db2()
        # act
        cur.execute("SELECT * FROM test WHERE a LIKE 'á__'")

        self._check_result(cur, {'ábc', 'ÁBC'})

    def test_like_escape_supports_unicode(self):
        cur = self._simple_db2()
        x = 'áb%c_def'
        cur.execute('INSERT INTO test VALUES (?)', (x,))
        # act
        cur.execute("SELECT * FROM test WHERE a LIKE 'áb/%_/_%' ESCAPE '/'")

        self._check_result(cur, {x})

    def test_case_mapping(self):
        conn = sqlite_ucf.connect(':memory:', unicode_case_folding=True)
        cur = conn.cursor()
        cur.execute('CREATE TABLE test (a text)')
        cur.execute('INSERT INTO test VALUES (?)', ('start',))

        for i, word in enumerate(unicode_chunks()):
            if i == 0:
                continue
            cur.execute('UPDATE test SET a = ?', (word,))
            db_lower = cur.execute('SELECT lower(a) FROM test').fetchone()[0]
            py_lower = word.lower()
            db_upper = cur.execute('SELECT upper(a) FROM test').fetchone()[0]
            py_upper = word.upper()
            self.assertEqual(db_lower, py_lower, 'lower words differ at chunk {}'.format(i))
            self.assertEqual(db_upper, py_upper, 'upper words differ at chunk {}'.format(i))

    def test_old_behaviour_when_true(self):
        cur = self._simple_db(unicode_case_folding=False)

        cur.execute("SELECT * FROM test WHERE a = 'á'")
        self._check_result(cur, {'á'})

        cur.execute('SELECT LOWER(a) FROM test')
        self._check_result(cur, {'a', 'á', 'Á'})

        cur.execute('SELECT UPPER(a) FROM test')
        self._check_result(cur, {'A', 'á', 'Á'})

    def test_module_default(self):
        sqlite_ucf.unicode_case_folding_default = True
        conn = sqlite_ucf.connect(':memory:')
        cur = conn.cursor()
        cur.execute('CREATE TABLE test (a text COLLATE NOCASE)')
        cur.executemany('INSERT INTO test VALUES (?)', [(x,) for x in ['Á', 'á']])

        cur.execute('SELECT UPPER(a) FROM test')
        self._check_result(cur, {'Á'})

        cur.execute('SELECT LOWER(a) FROM test')
        self._check_result(cur, {'á'})
