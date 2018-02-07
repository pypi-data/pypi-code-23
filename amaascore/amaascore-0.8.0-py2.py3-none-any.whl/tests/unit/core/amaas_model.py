from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.core.amaas_model import AMaaSModel


class AMaaSModelTest(unittest.TestCase):

    def test_Version(self):
        model = AMaaSModel(version='1')
        self.assertEqual(type(model.version), int)
        self.assertEqual(model.version, 1)


if __name__ == '__main__':
    unittest.main()
