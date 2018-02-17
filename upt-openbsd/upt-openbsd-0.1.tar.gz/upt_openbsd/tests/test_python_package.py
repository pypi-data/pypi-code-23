# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest


import upt
from upt_openbsd.upt_openbsd import OpenBSDPythonPackage


class TestOpenBSDPythonPackage(unittest.TestCase):
    def setUp(self):
        self.obsd_pkg = OpenBSDPythonPackage()

    def test_pkgname(self):
        expected = 'py-foo-${MODPY_EGG_VERSION}'

        self.obsd_pkg.upt_pkg = upt.Package('python-foo', '3.14')
        self.assertEqual(self.obsd_pkg._pkgname(), expected)

        self.obsd_pkg.upt_pkg = upt.Package('foo', '3.14')
        self.assertEqual(self.obsd_pkg._pkgname(), expected)


if __name__ == '__main__':
    unittest.main()
