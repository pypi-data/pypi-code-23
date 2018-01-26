# -*- coding: utf-8 -*-

### imports ###################################################################
import unittest

### local imports from ########################################################
from qvpy.dotdict import DictWithAttributes, substitute


###############################################################################
class TestDictWithAttribs(unittest.TestCase):

    myDict = {
        'a': 1,
        'b': '$x + 123',
        'c': {'d1': '$x', 'd2': '2 * $y'}
    }

    d = DictWithAttributes(myDict)

    def test_00_init(self):
        d = TestDictWithAttribs.d

        self.assertEqual(d['a'], d.a)
        self.assertEqual(d['b'], d.b)
        self.assertEqual(d['c'], d.c)

    def test_01_substitute(self):
        d = TestDictWithAttribs.d
        subst = {'x': 100, 'y': 3.14}

        substitute(d, subst)

        self.assertEqual(d['a'], d.a)
        self.assertNotEqual(d['b'], d.b)
        self.assertEqual(d['c'], d.c)
