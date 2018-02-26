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
        names = ['python-foo', 'py-foo', 'pyfoo', 'pyFoo']
        for name in names:
            self.obsd_pkg.upt_pkg = upt.Package(name, '13.37')
            self.assertEqual(self.obsd_pkg._pkgname(), expected)

        self.obsd_pkg.upt_pkg = upt.Package('py', '13.37')
        self.assertEqual(self.obsd_pkg._pkgname(),
                         'py-py-${MODPY_EGG_VERSION}')


if __name__ == '__main__':
    unittest.main()
