# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_openbsd.upt_openbsd import OpenBSDPackage


class TestOpenBSDPackageWithoutSQLPorts(unittest.TestCase):
    def setUp(self):
        OpenBSDPackage.SQLPORTS_DB = '/does/not/exist'

    def test_sqlports_init(self):
        with OpenBSDPackage() as package:
            self.assertIsNone(package.conn)

    def test_sqlports_fullpkgpath(self):
        with OpenBSDPackage() as package:
            out = package._to_openbsd_fullpkgpath('py-requests')
            expected = 'xxx/py-requests'
            self.assertEqual(out, expected)


class TestOpenBSDPackageWithSQLPorts(unittest.TestCase):
    def setUp(self):
        OpenBSDPackage.SQLPORTS_DB = ':memory:'
        self.package = OpenBSDPackage()
        self.package.conn.execute('''CREATE TABLE IF NOT EXISTS `Ports` (
    `FULLPKGPATH` TEXT NOT NULL UNIQUE,
    `PKGSPEC`	  TEXT
)''')
        self.package.conn.execute('''INSERT INTO PORTS VALUES (
    "www/py-flask", "py-flask-*"
)''')
        self.package.conn.commit()

    def test_pkgspec_not_found(self):
        out = self.package._to_openbsd_fullpkgpath('py-requests')
        expected = 'xxx/py-requests'
        self.assertEqual(out, expected)

    def test_pkgspec_found(self):
        out = self.package._to_openbsd_fullpkgpath('py-flask')
        expected = 'www/py-flask'
        self.assertEqual(out, expected)

    def tearDown(self):
        self.package.conn.close()


class TestOpenBSDPackageLicenses(unittest.TestCase):
    def setUp(self):
        self.package = OpenBSDPackage()
        self.package.upt_pkg = upt.Package('foo', '42')

    def test_no_licenses(self):
        self.package.upt_pkg.licenses = []
        out = self.package._licenses()
        expected = '# TODO: check licenses'
        self.assertEqual(out, expected)

    def test_one_license(self):
        self.package.upt_pkg.licenses = [upt.licenses.BSDThreeClauseLicense()]
        out = self.package._licenses()
        expected = '# BSD-3-Clause'
        self.assertEqual(out, expected)

    def test_multiple_license(self):
        self.package.upt_pkg.licenses = [
            upt.licenses.BSDTwoClauseLicense(),
            upt.licenses.BSDThreeClauseLicense()
        ]
        out = self.package._licenses()
        expected = '# BSD-2-Clause\n# BSD-3-Clause'
        self.assertEqual(out, expected)


if __name__ == '__main__':
    unittest.main()
