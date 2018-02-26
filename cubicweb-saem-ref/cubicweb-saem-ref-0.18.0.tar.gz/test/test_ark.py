# copyright 2018 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as publishged by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref tests for ARK identifier generation."""

from unittest import TestCase

import psycopg2
import psycopg2.errorcodes

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    testlib,
)

from cubicweb_saem_ref.ark import (
    ARK_RGX,
    insert_ark,
    match as ark_match,
)
import testutils


def setUpModule():
    testutils.startpgcluster(__file__)


class ArkRgxTC(TestCase):

    def test_syntax(self):
        """Make string interpolation is correct."""
        self.assertEqual(
            ARK_RGX.pattern,
            r'^(ark:/)?(?P<naan>\d+)/(?P<name>rf\w{7}g)(/(?P<qualifier>.{10}))?$',
        )

    def test(self):
        match = ark_match('ark:/12345/rf%sg' % ('q' * 7))
        self.assertTrue(match)
        self.assertEqual(match.group('naan'), '12345')
        self.assertEqual(match.group('name'), 'rfqqqqqqqg')

    def test_ext(self):
        match = ark_match('ark:/12345/name', external=True)
        self.assertTrue(match)
        self.assertEqual(match.group('naan'), '12345')
        self.assertEqual(match.group('name'), 'name')

    def test_no_scheme(self):
        match = ark_match('12345/rf%sg' % ('q' * 7))
        self.assertTrue(match)
        self.assertEqual(match.group('naan'), '12345')
        self.assertEqual(match.group('name'), 'rfqqqqqqqg')

    def test_ext_no_scheme(self):
        match = ark_match('12345/name', external=True)
        self.assertTrue(match)
        self.assertEqual(match.group('naan'), '12345')
        self.assertEqual(match.group('name'), 'name')

    def test_qualified(self):
        ark = '0/rfr8hps6ng/h4050n4j02'
        match = ark_match(ark)
        self.assertTrue(match)
        self.assertEqual(match.group('naan'), '0')
        self.assertEqual(match.group('name'), 'rfr8hps6ng')
        self.assertEqual(match.group('qualifier'), 'h4050n4j02')

    def test_ext_qualified(self):
        ark = '666/name/qualifier'
        match = ark_match(ark, external=True)
        self.assertTrue(match)
        self.assertEqual(match.group('naan'), '666')
        self.assertEqual(match.group('name'), 'name')
        self.assertEqual(match.group('qualifier'), 'qualifier')

    def test_tesutils_match_ark_qualified(self):
        ark = '0/rfr8hps6ng/h4050n4j02'

        def check(match):
            self.assertTrue(match)
            self.assertEqual(match.group(1), '/h4050n4j02')

        check(testutils.match_ark(ark))
        check(testutils.match_ark_uri('ark:/' + ark))


class ArkServiceTC(testlib.CubicWebTC):
    # This could be a plain unittest.TestCase as we don't use CubicWeb's
    # database. But on the other hand, CubicWebTC makes it easier to get a
    # postgres configuration handling setup/teardown.

    configcls = PostgresApptestConfiguration

    def connect(self):
        return self.repo.system_source.get_connection()

    def test_unique_generated(self):
        """We should be able to produce 20 ARK identifiers of length 4 with a
        2-characters prefix and 1 control character.
        """
        n = 20
        arks = []
        with self.connect() as conn:
            with conn.cursor() as cu:
                for _ in range(n):
                    cu.execute("SELECT * from gen_ark(%s, %s, %s, %s, %s);",
                               (0, 4, 'rf', 'x', 10))
                    arks.append(cu.fetchone()[0])
                    conn.commit()
                cu.execute("SELECT * from ark")
                r = cu.fetchall()
        self.assertEqual(len(set(r)), n, len(r))
        self.assertCountEqual([ark for _, ark, _ in r], arks)

    def test_gen_ark_maxit(self):
        with self.connect() as conn:
            with conn.cursor() as cu:
                with self.assertRaises(psycopg2.InternalError) as cm:
                    cu.execute("SELECT * from gen_ark(%s, %s, %s, %s, %s);",
                               (0, 4, 'rf', 'x', 0))
                exc = cm.exception
                self.assertEqual(psycopg2.errorcodes.lookup(exc.pgcode),
                                 'ASSERT_FAILURE')
                self.assertIn('maximum number of iterations: 0',
                              str(exc))

    def test_gen_qualified_ark_maxit(self):
        with self.connect() as conn:
            with conn.cursor() as cu:
                cu.execute("INSERT INTO ark VALUES (%s, %s, DEFAULT);",
                           (0, "parent", ))
                conn.commit()
                with self.assertRaises(psycopg2.InternalError) as cm:
                    cu.execute("SELECT * from gen_qualified_ark(%s, %s, %s, %s);",
                               (0, "parent", 7, 0))
                exc = cm.exception
                self.assertEqual(psycopg2.errorcodes.lookup(exc.pgcode),
                                 'ASSERT_FAILURE')
                self.assertIn('maximum number of iterations: 0',
                              str(exc))

    def test_qualifier(self):
        def insert(qualifier=None):
            with self.connect() as conn:
                with conn.cursor() as cu:
                    cu.execute("INSERT INTO ark VALUES (%s, %s, %s);",
                               (0, "he", qualifier))
        insert("ah")
        with self.assertRaises(psycopg2.IntegrityError) as cm:
            insert("ah")
        self.assertIn(
            'duplicate key value violates unique constraint',
            str(cm.exception),
        )
        insert("he")

    def test_dup(self):
        def insert():
            with self.connect() as conn:
                with conn.cursor() as cu:
                    cu.execute("INSERT INTO ark VALUES (42, 'he', 'aha');")
        insert()
        with self.assertRaises(psycopg2.IntegrityError) as cm:
            insert()
        self.assertIn(
            'duplicate key value violates unique constraint',
            str(cm.exception),
        )

    def test_generate_qualifier_no_name_existing(self):
        with self.connect() as conn:
            with conn.cursor() as cu:
                with self.assertRaises(psycopg2.DataError) as cm:
                    cu.execute("SELECT * FROM gen_qualified_ark(%s, %s, %s, 20);",
                               (1, "doesnotexist", 3))
        self.assertIn('no ark record matching "1/doesnotexist" found',
                      str(cm.exception))

    def test_generate_qualifier_name_existing(self):
        with self.connect() as conn:
            with conn.cursor() as cu:
                cu.execute("INSERT INTO ark VALUES (%s, %s, DEFAULT);",
                           (12345, "exists", ))
                cu.execute("SELECT * FROM gen_qualified_ark(%s, %s, %s, 20);",
                           (12345, "exists", 3))
                cu.execute("SELECT * FROM ark"
                           " WHERE ark.naan = 12345 AND ark.name = 'exists'"
                           " AND NOT ark.qualifier = '';")
                (_, _, qualifier), = cu.fetchall()
        self.assertEqual(len(qualifier), 3, qualifier)

    def test_insert_ark(self):
        with self.admin_access.cnx() as cnx:
            ark = insert_ark(cnx, '12345', u'bob')
            cnx.commit()
            self.assertEqual(ark, u'12345/bob')
            results = cnx.system_sql('SELECT naan, name, qualifier FROM ark;').fetchall()
            self.assertEqual(results, [(12345, u'bob', u'')])

    def test_insert_ark_qualifier(self):
        with self.admin_access.cnx() as cnx:
            ark = insert_ark(cnx, '12345', u'bob', u'1')
            cnx.commit()
            self.assertEqual(ark, u'12345/bob/1')
            results = cnx.system_sql('SELECT naan, name, qualifier FROM ark;').fetchall()
            self.assertEqual(results, [(12345, u'bob', u'1')])


if __name__ == '__main__':
    import unittest
    unittest.main()
