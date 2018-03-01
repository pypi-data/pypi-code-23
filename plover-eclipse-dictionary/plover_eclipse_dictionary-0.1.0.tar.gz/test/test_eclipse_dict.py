# Copyright (c) 2018 Open Steno Project
# See LICENSE.txt for details.
# Eclipse (.dix) handler tests
# written by Marnanel Thurman <marnanel@thurman.org.uk>

import os
import codecs
import unittest
from plover_eclipse_dictionary import EclipseDictionary
from collections import defaultdict

FILENAME = 'test/eclipse-test.dix'

EXPECTED = {
    ('U', 'SURP'): 'usurp',
    ('U', 'SKWRA*EU', 'AES'): "you Jay's",
    ('U', 'SPHAOEPB'): 'you mean so',
    ('U', 'SRA*E'): 'you have a',
    ('U', 'SRA*U'): 'you have a',
    ('U', 'STAEUGS'): 'eustachian',
    ('U', 'STRAOEUF', 'TO'): 'you strive to',
    ('U', 'SURP'): 'usurp',
    ('U', 'TKPWAOEUGS'): 'you guys',
    ('U', 'TKROUS', 'KWREU'): 'you drowsy',
    ('UD',): "you'd",
    ('UD', '*ER'): 'udder',
    ('UD', 'EL'): 'Udell',
    ('UD', 'ER'): 'udder',
    ('UD', 'ERS'): 'udders',
    ('UZ', 'PWEBG', 'STAPB'): 'Uzbekistan',
}

class TestCase(unittest.TestCase):

    def test_load_dictionary(self):

        d = EclipseDictionary.load(FILENAME)

    def test_getitem(self):
        d = EclipseDictionary.load(FILENAME)

        for (k, v) in sorted(EXPECTED.items()):
            self.assertEqual(d[k], v)

            self.assertEqual(d.__getitem__(k), v)

            self.assertEqual(d.get(k), v)

            self.assertEqual(d.get(k, 'dummy'), v)

        self.assertEqual(d.get('NOT REALLY A KEY', 'dummy'),
            'dummy')

    def test_reverse_lookup(self):
        d = EclipseDictionary.load(FILENAME)

        INV_EXPECTED = defaultdict(list)

        for k, v in EXPECTED.items():
            INV_EXPECTED[v].append(k)

        for v, keylist in sorted(INV_EXPECTED.items()):
            self.assertEqual(d.reverse_lookup(v), keylist)

