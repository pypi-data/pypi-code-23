import os
import sys
import unittest
import ocraccuracyreporter.oar as oar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class oartests(unittest.TestCase):

    def test_print(self):
        oreport = oar(expected='john', given='joh', label='name')
        self.assertEqual(oreport.__str__(), 'name,john,joh,86,100,86,86,94,1')
