# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest


import upt
from upt_guix.upt_guix import GuixPackage


class TestGuixPackage(unittest.TestCase):
    def setUp(self):
        self.guix_pkg = GuixPackage()

    def test_synopsis(self):
        self.guix_pkg.upt_pkg = upt.Package('foo', '42')

        self.guix_pkg.upt_pkg.summary = 'A framework'
        self.assertEqual(self.guix_pkg._synopsis(), 'Framework')

        self.guix_pkg.upt_pkg.summary = 'a framework'
        self.assertEqual(self.guix_pkg._synopsis(), 'Framework')

        self.guix_pkg.upt_pkg.summary = 'An animal'
        self.assertEqual(self.guix_pkg._synopsis(), 'Animal')

        self.guix_pkg.upt_pkg.summary = 'an animal'
        self.assertEqual(self.guix_pkg._synopsis(), 'Animal')

        self.guix_pkg.upt_pkg.summary = 'No period.'
        self.assertEqual(self.guix_pkg._synopsis(), 'No period')

        self.guix_pkg.upt_pkg.summary = 'thing'
        self.assertEqual(self.guix_pkg._synopsis(), 'Thing')


if __name__ == '__main__':
    unittest.main()
