# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest


import upt
from upt_guix.upt_guix import Guix


class TestGuixBackend(unittest.TestCase):
    def setUp(self):
        self.guix = Guix()

    def test_unhandled_frontend(self):
        upt_pkg = upt.Package('foo', '42')
        upt_pkg.frontend = 'invalid backend'
        with self.assertRaises(upt.UnhandledFrontendError):
            self.guix.create_package(upt_pkg)


if __name__ == '__main__':
    unittest.main()
