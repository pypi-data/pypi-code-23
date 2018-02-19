# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest


from upt_guix.upt_guix import GuixPythonPackage


class TestGuixPythonPackage(unittest.TestCase):
    def setUp(self):
        self.guix_pkg = GuixPythonPackage

    def test_guix_name(self):
        self.assertEqual(self.guix_pkg._guix_name('requests'),
                         'python-requests')
        self.assertEqual(self.guix_pkg._guix_name('python-dateutil'),
                         'python-dateutil')


if __name__ == '__main__':
    unittest.main()
